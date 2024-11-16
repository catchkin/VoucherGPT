import os
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database, drop_database

def reset_database(db_url: str):
    """데이터베이스 초기화 및 재생성"""
    # DB 존재 시 삭제
    if database_exists(db_url):
        drop_database(db_url)

    # DB 생성
    create_database(db_url)

    # Alembic 마이그레이션 실행
    subprocess.run(['alembic', 'upgrade', 'head'])

if __name__ == "__main__":
    # 환경변수에서 DB URL 가져오기
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    reset_database(db_url)
