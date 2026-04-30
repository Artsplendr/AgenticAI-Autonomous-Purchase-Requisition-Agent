"""Application settings loaded from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    anthropic_api_key: str = ""
    llm_provider: str = "anthropic"  # anthropic
    llm_model: str = "claude-sonnet-4-6"
    llm_max_tokens: int = 1000
    auto_approval_threshold: float = 5000
    price_weight: float = 0.5
    delivery_weight: float = 0.3
    reliability_weight: float = 0.2


settings = Settings()
