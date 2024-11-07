# app/core/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://vouchergpt_user:blogcodi0318@localhost:5432/vouchergpt"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 설정 인스턴스 생성
settings = Settings()