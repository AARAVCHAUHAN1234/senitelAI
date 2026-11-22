"""Application settings loaded from environment variables."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the SentinelAI backend."""

    DATABASE_URL: str = "sqlite:///./sentinel.db"
    ENABLED_MODULES: str = "all"
    CORS_ORIGINS: str = "*"
    VOYAGESIM_URL: str = "http://localhost:8001"
    GEMINI_API_KEY: Optional[str] = None
    DEMO_TOKEN: str = "sentinel-demo-token"

    @property
    def enabled_module_list(self) -> list[str]:
        raw = self.ENABLED_MODULES.strip()
        if raw.lower() == "all":
            return ["all"]
        return [m.strip() for m in raw.split(",") if m.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
