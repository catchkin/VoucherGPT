from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoucherGPT"
    DATABASE_URL: str
    OPENAI_API_KEY: str
    MODEL_NAME: str = "gpt-4"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()