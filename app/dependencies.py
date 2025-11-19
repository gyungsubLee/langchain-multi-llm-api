"""
FastAPI 의존성 주입
"""
from fastapi import Depends
from app.core.config import settings
from app.repositories.vector_db_repository import VectorDBRepository
from app.services.vector_db_service import VectorDBService


def get_vector_db_repository() -> VectorDBRepository:
    """벡터 DB 저장소 의존성"""
    return VectorDBRepository(vector_db_dir=settings.VECTOR_DB_DIR)


def get_vector_db_service(
    repository: VectorDBRepository = Depends(get_vector_db_repository)
) -> VectorDBService:
    """벡터 DB 서비스 의존성"""
    return VectorDBService(repository=repository)
