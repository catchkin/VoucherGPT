from typing import Any, Dict, Optional
from pydantic import (
    BaseSettings,
    PostgreDsn,
    validator,
    DirectoryPath
)
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # JWT Token settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: PostgreDsn
    ASYNC_DATABASE_URL: Optional[str] = None

    @validator("ASYNC_DATABASE_URL", pre=True)
    def assemble_async_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v:
            return v
        db_url = values.get("DATABASE_URL")
        return str(db_url).replace("postgresql://", "postgresql+asyncpg://") if db_url else None

    # OpenAI
    OpenAI_API_KEY: str
    GPT_MODE: str = "gpt-4-1106-preview"

    # File Upload
    UPLOAD_DIR:  DirectoryPath
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v: str) -> Path:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
