"""
API v4 - Retrieval & RAG Endpoints
클린 아키텍처 적용: 라우터는 요청/응답만 처리
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List

from app.models.schemas import (
    QueryRequest,
    RAGRequest,
    DocumentResponse,
    RAGResponse,
    UploadResponse,
    VectorDBListResponse,
    VectorDBDetailResponse,
    DeleteResponse
)
from app.services.vector_db_service import VectorDBService
from app.dependencies import get_vector_db_service
from app.core.config import settings

router = APIRouter(prefix="/v4", tags=["v4-retrieval-rag"])


@router.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db_name: str = "default",
    service: VectorDBService = Depends(get_vector_db_service)
):
    """
    PDF 파일 업로드 및 벡터 DB 생성

    Args:
        file: 업로드할 PDF 파일
        db_name: 저장할 벡터 DB 이름 (기본값: default)
        service: 벡터 DB 서비스 (의존성 주입)
    """
    if settings.MOCK:
        return UploadResponse(
            status="success",
            filename=file.filename,
            db_name=db_name,
            pages=0,
            chunks=42,
            method="RecursiveCharacterTextSplitter",
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            saved_to=f"vector_db/{db_name}"
        )

    try:
        return await service.upload_pdf(file, db_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")


@router.post("/search", response_model=List[DocumentResponse])
async def search_documents(
    req: QueryRequest,
    service: VectorDBService = Depends(get_vector_db_service)
):
    """
    벡터 데이터베이스에서 문서 검색
    """
    if settings.MOCK:
        return [
            DocumentResponse(
                content=f"[MOCK] 검색 결과 {i+1}: '{req.query}'에 대한 관련 문서입니다.",
                metadata={"source": f"mock_doc_{i+1}.pdf", "page": i},
                score=0.95 - i * 0.1
            )
            for i in range(req.top_k)
        ]

    try:
        return service.search_documents(
            query=req.query,
            top_k=req.top_k,
            db_name=req.db_name
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Vector DB '{req.db_name}' not found. Please upload a PDF first using /v4/upload-pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")


@router.post("/rag", response_model=RAGResponse)
async def rag_query(
    req: RAGRequest,
    service: VectorDBService = Depends(get_vector_db_service)
):
    """
    RAG (Retrieval-Augmented Generation) 쿼리
    문서 검색 + LLM 답변 생성
    """
    if settings.MOCK:
        mock_sources = [
            DocumentResponse(
                content=f"[MOCK] 관련 문서 {i+1}",
                metadata={"source": f"mock_source_{i+1}.pdf", "page": i},
                score=0.9 - i * 0.1
            )
            for i in range(req.top_k)
        ]

        return RAGResponse(
            query=req.query,
            answer=f"[MOCK RAG] '{req.query}'에 대한 답변입니다. {req.top_k}개의 문서를 참고했습니다.",
            source_documents=mock_sources
        )

    try:
        return service.rag_query(
            query=req.query,
            top_k=req.top_k,
            db_name=req.db_name
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Vector DB '{req.db_name}' not found. Please upload a PDF first using /v4/upload-pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {e}")


@router.get("/list-dbs", response_model=VectorDBListResponse)
async def list_vector_dbs(
    service: VectorDBService = Depends(get_vector_db_service)
):
    """저장된 모든 벡터 DB 목록 조회"""
    try:
        return service.list_databases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List error: {e}")


@router.get("/db-info/{db_name}", response_model=VectorDBDetailResponse)
async def get_db_info(
    db_name: str,
    service: VectorDBService = Depends(get_vector_db_service)
):
    """특정 벡터 DB 정보 조회"""
    try:
        return service.get_database_info(db_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Vector DB '{db_name}' not found"
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Info error: {e}")


@router.delete("/delete-db/{db_name}", response_model=DeleteResponse)
async def delete_vector_db(
    db_name: str,
    service: VectorDBService = Depends(get_vector_db_service)
):
    """벡터 DB 삭제"""
    try:
        return service.delete_database(db_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Vector DB '{db_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {e}")
