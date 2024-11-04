from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoucherGPT"
    DATABASE_URL: str
    OPENAI_API_KEY: str
    MODEL_NAME: str = "gpt-4"

    class Config:
        env_file = ".env"

settings = Settings()