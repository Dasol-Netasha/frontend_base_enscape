from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = "postgresql+psycopg://base_user:base_pass@localhost:5432/base_db"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = True


settings = Settings()