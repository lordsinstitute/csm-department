"""Application configuration powered by environment variables."""

from functools import lru_cache
from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised settings object so services can access external credentials."""

    auth0_domain: Optional[str] = Field(default=None, description="Auth0 tenant domain for auth flows.")
    auth0_client_id: Optional[str] = Field(
        default=None,
        description="Auth0 application identifier used by the frontend.",
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key leveraged for adversarial planning.",
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash-thinking-exp-1219",  # Updated model
        description="Gemini model identifier used when generating AI insights.",
    )
    github_token: Optional[str] = Field(
        default=None,
        description="Optional GitHub personal access token used when fetching repositories.",
    )
    snowflake_account: Optional[str] = Field(
        default=None,
        description="Snowflake account locator when integrating with the real warehouse.",
        validation_alias=AliasChoices("COGNITOFORGE_SNOWFLAKE_ACCOUNT", "SNOWFLAKE_ACCOUNT"),
    )
    snowflake_user: Optional[str] = Field(
        default=None,
        description="Snowflake user credential used for authenticated connections.",
        validation_alias=AliasChoices("COGNITOFORGE_SNOWFLAKE_USER", "SNOWFLAKE_USER"),
    )
    snowflake_password: Optional[str] = Field(
        default=None,
        description="Snowflake password associated with the configured user.",
        validation_alias=AliasChoices("COGNITOFORGE_SNOWFLAKE_PASSWORD", "SNOWFLAKE_PASSWORD"),
    )
    snowflake_warehouse: Optional[str] = Field(
        default=None,
        description="Target Snowflake warehouse for query execution.",
        validation_alias=AliasChoices("COGNITOFORGE_SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_WAREHOUSE"),
    )
    snowflake_database: Optional[str] = Field(
        default=None,
        description="Snowflake database containing CognitoForge artefacts.",
        validation_alias=AliasChoices("COGNITOFORGE_SNOWFLAKE_DATABASE", "SNOWFLAKE_DATABASE"),
    )
    snowflake_schema: Optional[str] = Field(
        default=None,
        description="Snowflake schema where simulation tables are managed.",
        validation_alias=AliasChoices("COGNITOFORGE_SNOWFLAKE_SCHEMA", "SNOWFLAKE_SCHEMA"),
    )
    use_gemini: bool = Field(
        default=False,
        description="Toggle to enable real Gemini integration when credentials are available.",
    )

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_prefix="COGNITOFORGE_",
        extra="allow",
        populate_by_name=True,
    )

    # ------------------------------------------------------------------
    # Supabase / Postgres (Option B – DB_* env vars)
    # ------------------------------------------------------------------

    supabase_db_host: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DB_HOST"),
        description="Supabase Postgres host",
    )

    supabase_db_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DB_NAME"),
        description="Supabase Postgres database name",
    )

    supabase_db_user: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DB_USER"),
        description="Supabase Postgres user",
    )

    supabase_db_password: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DB_PASSWORD"),
        description="Supabase Postgres password",
    )

    supabase_db_port: Optional[int] = Field(
        default=5432,
        validation_alias=AliasChoices("DB_PORT"),
        description="Supabase Postgres port",
    )



@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance so every import shares the same configuration."""

    return Settings()
