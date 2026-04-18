"""
Groq + Sentence-Transformers client.
Drop-in replacement for the previous ollama_client.py.

- embed()    → sentence-transformers (nomic-embed-text, 768-dim, CPU-friendly)
- generate() → Groq API (llama-3.3-70b-versatile)

Install deps:
    pip install groq sentence-transformers

Environment:
    GROQ_API_KEY=<your key>
"""

import os
import threading
from typing import List
import logging

# Load .env file if present (handles local dev and most deployment setups)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed — env vars must be set externally

logging.getLogger("safetensors").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

# ── Groq ──────────────────────────────────────────────────────────────────────
from groq import Groq

_groq_client: Groq | None = None
_groq_lock = threading.Lock()

DEFAULT_MODEL = "llama-3.3-70b-versatile"   # fast, high quality
FALLBACK_MODEL = "llama3-8b-8192"            # cheaper fallback


def _get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        with _groq_lock:
            if _groq_client is None:
                api_key = os.environ.get("GROQ_API_KEY")
                if not api_key:
                    raise EnvironmentError(
                        "GROQ_API_KEY environment variable is not set. "
                        "Get a free key at https://console.groq.com"
                    )
                _groq_client = Groq(api_key=api_key)
    return _groq_client


def generate(model: str, prompt: str) -> str:
    """
    Generate a response from Groq.

    Args:
        model:  Ignored for compatibility — we always use Groq's hosted models.
                Pass any string; the actual model is controlled by DEFAULT_MODEL.
        prompt: Full prompt string (system + context already embedded).

    Returns:
        Generated text as a plain string.
    """
    client = _get_groq_client()

    # The old API received a single combined prompt string.
    # Groq expects chat-style messages; we treat the whole thing as a user message.
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert code assistant. "
                "Answer clearly and accurately, referencing specific code when possible."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=2048,
            temperature=0.2,   # low temp → deterministic, accurate code answers
        )
        return response.choices[0].message.content or ""

    except Exception as primary_error:
        print(f"⚠️  Groq primary model failed ({primary_error}), retrying with fallback…")
        try:
            response = client.chat.completions.create(
                model=FALLBACK_MODEL,
                messages=messages,
                max_tokens=2048,
                temperature=0.2,
            )
            return response.choices[0].message.content or ""
        except Exception as fallback_error:
            raise RuntimeError(
                f"Both Groq models failed.\n"
                f"Primary: {primary_error}\n"
                f"Fallback: {fallback_error}"
            ) from fallback_error


# ── Sentence-Transformers Embeddings ─────────────────────────────────────────
# We use 'nomic-ai/nomic-embed-text-v1' which:
#   • Produces 768-dim vectors  (same as your existing FAISS indices)
#   • Runs on CPU, no GPU needed
#   • Matches the semantic quality of typical Ollama embedding models
#   • Is free and open-source

_embed_model = None
_embed_lock = threading.Lock()


# BAAI/bge-base-en-v1.5:
#   • 768-dim output  (matches existing FAISS indices)
#   • No extra deps   (no einops, no triton, plain sentence-transformers)
#   • Top-tier quality for code + text retrieval on MTEB benchmarks
EMBED_MODEL_NAME = "BAAI/bge-base-en-v1.5"
EMBED_DIM = 768


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        with _embed_lock:
            if _embed_model is None:
                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError as e:
                    raise ImportError(
                        "sentence-transformers is required for embeddings. "
                        "Install it with: pip install sentence-transformers"
                    ) from e

                print(f"⏳ Loading embedding model '{EMBED_MODEL_NAME}' (first run only)…")
                _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
                print(f"✅ Embedding model loaded (dim={EMBED_DIM})")
    return _embed_model


def embed(text: str) -> List[float]:
    """
    Embed a single text string (for indexing documents/chunks).

    BGE models perform best with an instruction prefix on the document side.
    Returns a list of 768 floats.
    """
    model = _get_embed_model()
    # BGE recommends this prefix for passage/document embedding
    prefixed = f"Represent this code for retrieval: {text}"
    vector = model.encode(prefixed, normalize_embeddings=True)
    return vector.tolist()


def embed_query(text: str) -> List[float]:
    """
    Embed a *query* string for retrieval.
    BGE uses a different instruction prefix for queries vs documents.
    """
    model = _get_embed_model()
    # BGE recommended query prefix
    prefixed = f"Represent this question for searching relevant code: {text}"
    vector = model.encode(prefixed, normalize_embeddings=True)
    return vector.tolist()


__all__ = ["generate", "embed", "embed_query", "DEFAULT_MODEL", "EMBED_DIM"]