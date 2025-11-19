"""
애플리케이션 설정 관리
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    # API 설정
    MOCK: bool = True
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    GOOGLE_MODEL: Optional[str] = None
    ANTHROPIC_MODEL: Optional[str] = None

    # 벡터 DB 설정
    VECTOR_DB_DIR: Path = Path("vector_db")
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    DEFAULT_TOP_K: int = 3

    # PDF 처리 설정
    TEXT_SPLITTER_SEPARATORS: list[str] = ["\n\n", "\n", " ", ""]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 추가 필드 무시


# 싱글톤 인스턴스
settings = Settings()

# 벡터 DB 디렉토리 생성
settings.VECTOR_DB_DIR.mkdir(exist_ok=True)
