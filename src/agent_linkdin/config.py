from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openrouter_api_key: str
    tavily_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api"
    tavily_base_url: str = "https://api.tavily.com"
    research_model: str = "anthropic/claude-haiku-4-5"
    draft_model: str = "anthropic/claude-haiku-4-5"
    review_model: str = "anthropic/claude-haiku-4-5"
    output_dir: Path = Path("output")
    max_iterations: int = 2
    search_max_results: int = 5
    search_timeout_s: float = 15.0


def load_settings() -> Settings:
    return Settings()
