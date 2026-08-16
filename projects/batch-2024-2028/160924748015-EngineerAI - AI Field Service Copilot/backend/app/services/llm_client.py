import hashlib
import json
from pathlib import Path
from typing import Union

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import settings

CACHE_DIR = Path(__file__).resolve().parents[2] / "llm_cache"

UserContent = Union[str, list[dict]]


class LLMParseError(Exception):
    pass


class _RetryableStatusError(Exception):
    pass


async def call_llm(
    system_prompt: str,
    user_content: UserContent,
    schema: type[BaseModel],
    fixture_key: str | None = None,
) -> BaseModel:
    """Call the configured LLM, constrained to `schema`, with provider fallback and dev caching."""
    cache_key = None
    if settings.llm_cache:
        cache_key = _cache_key(settings.llm_model, system_prompt, user_content)
        cached = _read_cache(cache_key)
        if cached is not None:
            return schema.model_validate(cached)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    data = await _call_with_fallback(messages, schema)

    try:
        result = schema.model_validate(data)
    except ValidationError:
        messages.append({"role": "assistant", "content": json.dumps(data)})
        messages.append({"role": "user", "content": "Return ONLY valid JSON matching the schema."})
        data = await _call_with_fallback(messages, schema)
        try:
            result = schema.model_validate(data)
        except ValidationError as exc:
            raise LLMParseError(f"Could not parse LLM response into {schema.__name__}") from exc

    if cache_key is not None:
        _write_cache(cache_key, data)

    return result


async def _call_with_fallback(messages: list[dict], schema: type[BaseModel]) -> dict:
    try:
        return await _post_chat_completion(
            settings.llm_base_url, settings.llm_api_key, settings.llm_model, messages, schema
        )
    except (httpx.TimeoutException, _RetryableStatusError):
        if not settings.llm_fallback_base_url:
            raise
        return await _post_chat_completion(
            settings.llm_fallback_base_url,
            settings.llm_fallback_api_key,
            settings.llm_fallback_model,
            messages,
            schema,
        )


async def _post_chat_completion(
    base_url: str, api_key: str, model: str, messages: list[dict], schema: type[BaseModel]
) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": schema.model_json_schema(),
                "strict": True,
            },
        },
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )

    if response.status_code == 429 or response.status_code >= 500:
        raise _RetryableStatusError(f"{response.status_code}: {response.text}")
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def _cache_key(model: str, system_prompt: str, user_content: UserContent) -> str:
    hasher = hashlib.sha256()
    hasher.update(model.encode())
    hasher.update(system_prompt.encode())
    hasher.update(_serialize_user_content(user_content).encode())
    return hasher.hexdigest()


def _serialize_user_content(user_content: UserContent) -> str:
    if isinstance(user_content, str):
        return user_content

    parts = []
    for part in user_content:
        if part.get("type") == "image_url":
            url = part["image_url"]["url"]
            image_bytes = url.split(",", 1)[1] if "," in url else url
            parts.append({"type": "image_url", "sha256": hashlib.sha256(image_bytes.encode()).hexdigest()})
        else:
            parts.append(part)
    return json.dumps(parts, sort_keys=True)


def _read_cache(key: str) -> dict | None:
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _write_cache(key: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(data), encoding="utf-8")
