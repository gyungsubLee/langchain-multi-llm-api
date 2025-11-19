"""
API 요청/응답 스키마 정의
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# === 요청 스키마 ===

class QueryRequest(BaseModel):
    """문서 검색 요청"""
    query: str = Field(..., description="검색 쿼리")
    top_k: int = Field(default=3, ge=1, le=10, description="반환할 문서 수")
    db_name: str = Field(default="default", description="사용할 벡터 DB 이름")


class RAGRequest(BaseModel):
    """RAG 질의 요청"""
    query: str = Field(..., description="질문")
    top_k: int = Field(default=3, ge=1, le=10, description="참조할 문서 수")
    db_name: str = Field(default="default", description="사용할 벡터 DB 이름")


# === 응답 스키마 ===

class DocumentResponse(BaseModel):
    """문서 검색 결과"""
    content: str = Field(..., description="문서 내용")
    metadata: dict = Field(..., description="문서 메타데이터")
    score: Optional[float] = Field(None, description="유사도 점수")


class RAGResponse(BaseModel):
    """RAG 질의응답 결과"""
    query: str = Field(..., description="원본 질문")
    answer: str = Field(..., description="생성된 답변")
    source_documents: List[DocumentResponse] = Field(..., description="참조 문서")


class UploadResponse(BaseModel):
    """PDF 업로드 결과"""
    status: str
    filename: str
    db_name: str
    pages: int
    chunks: int
    method: str
    chunk_size: int
    chunk_overlap: int
    saved_to: str


class VectorDBInfo(BaseModel):
    """벡터 DB 정보"""
    name: str
    path: str
    size_bytes: int
    created: float
    modified: float


class VectorDBListResponse(BaseModel):
    """벡터 DB 목록 응답"""
    count: int
    databases: List[VectorDBInfo]


class VectorDBDetailResponse(BaseModel):
    """벡터 DB 상세 정보"""
    name: str
    path: str
    files: dict
    total_size_bytes: int
    total_size_mb: float
    created: float
    modified: float


class DeleteResponse(BaseModel):
    """삭제 결과"""
    status: str
    message: str
    deleted_path: str
