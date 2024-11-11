from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    field_validator,
    DirectoryPath,
    AnyHttpUrl,
    computed_field
)
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

    # Application Settings
    APP_NAME: str = "VoucherGPT"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # FastAPI backend
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Settings
    DATABASE_URL: str
    ASYNC_DATABASE_URL: Optional[str] = None

    # OpenAI Settings
    OPENAI_API_KEY: str
    GPT_MODEL: str = "gpt-4-1106-preview"

    # File Upload Settings
    UPLOAD_DIR: DirectoryPath
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
    ALLOWED_MIME_TYPES: list[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+psycopg2://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be a PostgreSQL connection string")
        return v

    @field_validator("ASYNC_DATABASE_URL", mode='before')
    def assemble_async_db_url(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        if v:
            return v
        db_url = info.data.get("DATABASE_URL")
        if not db_url:
            raise ValueError("Either ASYNC_DATABASE_URL or DATABASE_URL must be provided")
        return str(db_url).replace("postgresql://", "postgresql+asyncpg://")

    @field_validator("UPLOAD_DIR", mode='before')
    def create_upload_dir(cls, v: str) -> Path:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY should be at least 32 characters long")
        return v

    @computed_field
    @property
    def API_V1_URL(self) -> str:
        """Full URL for API v1 endpoint"""
        return f"{self.SERVER_HOST}{self.API_V1_STR}"


settings = Settings()