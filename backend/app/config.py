from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from pathlib import Path

# Always resolve .env relative to this file, regardless of working directory
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    # 兼容 Render 上未单独配置 service key 的情况，回退到 anon key
    supabase_service_key: str = Field(default="")

    # DeepSeek
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"

    # 智谱AI
    zhipu_api_key: str

    # JWT — 同时接受 JWT_SECRET 和 SECRET_KEY（兼容 Render 旧配置）
    jwt_secret: str = Field(default="", alias="jwt_secret")
    secret_key: str = Field(default="", alias="secret_key")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080

    # App
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    @property
    def effective_jwt_secret(self) -> str:
        """优先用 JWT_SECRET，没有则用 SECRET_KEY"""
        return self.jwt_secret or self.secret_key or "mindbase-fallback-secret"

    @property
    def effective_service_key(self) -> str:
        """优先用 SUPABASE_SERVICE_KEY，没有则降级用 SUPABASE_KEY"""
        return self.supabase_service_key or self.supabase_key

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {
        "env_file": str(_ENV_FILE),
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
