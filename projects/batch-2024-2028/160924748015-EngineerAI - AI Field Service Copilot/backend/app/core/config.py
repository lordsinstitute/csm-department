from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Root .env lives next to EngineerAI.md, three levels up from this file
# (backend/app/core/config.py -> backend/app -> backend -> project root).
_ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    llm_cache: bool = False

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Primary: Gemini API free tier, via its OpenAI-compatible endpoint.
    @property
    def llm_base_url(self) -> str:
        return "https://generativelanguage.googleapis.com/v1beta/openai/"

    @property
    def llm_api_key(self) -> str:
        return self.gemini_api_key

    @property
    def llm_model(self) -> str:
        return "gemini-2.5-flash"

    # Fallback: same model, paid, via OpenRouter. None if no OpenRouter key is set.
    @property
    def llm_fallback_base_url(self) -> str | None:
        return "https://openrouter.ai/api/v1" if self.openrouter_api_key else None

    @property
    def llm_fallback_api_key(self) -> str | None:
        return self.openrouter_api_key or None

    @property
    def llm_fallback_model(self) -> str:
        return "google/gemini-2.5-flash"


settings = Settings()
