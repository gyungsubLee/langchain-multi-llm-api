"""
API v4 - Retrieval & RAG Endpoints
최신 LangChain으로 마이그레이션된 문서 검색 및 RAG 기능
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import shutil
from pathlib import Path

router = APIRouter(prefix="/v4", tags=["v4-retrieval-rag"])

# 로컬 벡터 DB 저장 경로
VECTOR_DB_DIR = Path("vector_db")
VECTOR_DB_DIR.mkdir(exist_ok=True)


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    db_name: str = "default"  # 사용할 벡터 DB 이름


class DocumentResponse(BaseModel):
    content: str
    metadata: dict
    score: Optional[float] = None


class RAGRequest(BaseModel):
    query: str
    top_k: int = 3
    db_name: str = "default"  # 사용할 벡터 DB 이름


class RAGResponse(BaseModel):
    query: str
    answer: str
    source_documents: List[DocumentResponse]


MOCK = os.getenv("MOCK", "true").lower() == "true"


def load_vector_db(db_name: str):
    """로컬에 저장된 벡터 DB 로드"""
    db_path = VECTOR_DB_DIR / db_name

    if not db_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Vector DB '{db_name}' not found. Please upload a PDF first using /v4/upload-pdf"
        )

    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS

        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local(
            str(db_path),
            embeddings,
            allow_dangerous_deserialization=True
        )
        return db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load vector DB: {e}")


@router.post("/search", response_model=List[DocumentResponse])
async def search_documents(req: QueryRequest):
    """
    벡터 데이터베이스에서 문서 검색
    (최신 LangChain: FAISS + OpenAIEmbeddings)
    """
    if MOCK:
        return [
            DocumentResponse(
                content=f"[MOCK] 검색 결과 {i+1}: '{req.query}'에 대한 관련 문서입니다.",
                metadata={"source": f"mock_doc_{i+1}.pdf", "page": i},
                score=0.95 - i * 0.1
            )
            for i in range(req.top_k)
        ]

    try:
        # 로컬 벡터 DB 로드
        db = load_vector_db(req.db_name)
        retriever = db.as_retriever(search_kwargs={"k": req.top_k})

        # 최신 방식: invoke() 사용
        docs = retriever.invoke(req.query)

        return [
            DocumentResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                score=None  # FAISS는 기본적으로 score 미제공
            )
            for doc in docs
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")


@router.post("/rag", response_model=RAGResponse)
async def rag_query(req: RAGRequest):
    """
    RAG (Retrieval-Augmented Generation) 쿼리
    문서 검색 + LLM 답변 생성
    """
    if MOCK:
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
        from langchain_openai import ChatOpenAI
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains import create_retrieval_chain
        from langchain_core.prompts import ChatPromptTemplate
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing packages: {e}")

    try:
        # 로컬 벡터 DB 로드
        db = load_vector_db(req.db_name)
        retriever = db.as_retriever(search_kwargs={"k": req.top_k})

        # LLM 설정
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        llm = ChatOpenAI(model=model_name, temperature=0)

        # 프롬프트 템플릿
        system_prompt = """다음 문서를 참고하여 질문에 답변하세요.

        {context}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

        # Chain 생성 (최신 방식)
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # 실행
        result = rag_chain.invoke({"input": req.query})

        # 소스 문서 추출
        source_docs = [
            DocumentResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                score=None
            )
            for doc in result.get("context", [])
        ]

        return RAGResponse(
            query=req.query,
            answer=result["answer"],
            source_documents=source_docs
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {e}")


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), db_name: str = "default"):
    """
    PDF 파일 업로드 및 벡터 DB 생성
    (최신 RecursiveCharacterTextSplitter 사용)

    Args:
        file: 업로드할 PDF 파일
        db_name: 저장할 벡터 DB 이름 (기본값: default)
    """
    if MOCK:
        return {
            "status": "success",
            "filename": file.filename,
            "db_name": db_name,
            "message": "[MOCK] PDF가 업로드되고 벡터 DB에 추가되었습니다.",
            "chunks": 42,
            "method": "RecursiveCharacterTextSplitter",
            "saved_to": f"vector_db/{db_name}"
        }

    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing packages: {e}")

    try:
        # 임시 파일 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # PDF 로드
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()

        # 최신 방식: RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_documents(pages)

        # 벡터 DB 생성
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(chunks, embeddings)

        # 로컬에 벡터 DB 저장
        db_path = VECTOR_DB_DIR / db_name
        db.save_local(str(db_path))

        # 임시 파일 삭제
        os.unlink(tmp_path)

        return {
            "status": "success",
            "filename": file.filename,
            "db_name": db_name,
            "pages": len(pages),
            "chunks": len(chunks),
            "method": "RecursiveCharacterTextSplitter",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "saved_to": str(db_path)
        }

    except Exception as e:
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")


@router.get("/list-dbs")
async def list_vector_dbs():
    """저장된 모든 벡터 DB 목록 조회"""
    try:
        dbs = []
        for db_path in VECTOR_DB_DIR.iterdir():
            if db_path.is_dir():
                # index.faiss 파일이 있는지 확인
                index_file = db_path / "index.faiss"
                if index_file.exists():
                    db_info = {
                        "name": db_path.name,
                        "path": str(db_path),
                        "size_bytes": sum(f.stat().st_size for f in db_path.rglob('*') if f.is_file()),
                        "created": db_path.stat().st_ctime,
                        "modified": db_path.stat().st_mtime
                    }
                    dbs.append(db_info)

        return {
            "count": len(dbs),
            "databases": dbs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List error: {e}")


@router.delete("/delete-db/{db_name}")
async def delete_vector_db(db_name: str):
    """벡터 DB 삭제"""
    db_path = VECTOR_DB_DIR / db_name

    if not db_path.exists():
        raise HTTPException(status_code=404, detail=f"Vector DB '{db_name}' not found")

    try:
        shutil.rmtree(db_path)
        return {
            "status": "success",
            "message": f"Vector DB '{db_name}' has been deleted",
            "deleted_path": str(db_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {e}")


@router.get("/db-info/{db_name}")
async def get_db_info(db_name: str):
    """특정 벡터 DB 정보 조회"""
    db_path = VECTOR_DB_DIR / db_name

    if not db_path.exists():
        raise HTTPException(status_code=404, detail=f"Vector DB '{db_name}' not found")

    try:
        index_file = db_path / "index.faiss"
        pkl_file = db_path / "index.pkl"

        if not index_file.exists():
            raise HTTPException(status_code=500, detail=f"Invalid vector DB: missing index.faiss")

        total_size = sum(f.stat().st_size for f in db_path.rglob('*') if f.is_file())

        return {
            "name": db_name,
            "path": str(db_path),
            "files": {
                "index.faiss": index_file.stat().st_size if index_file.exists() else 0,
                "index.pkl": pkl_file.stat().st_size if pkl_file.exists() else 0
            },
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "created": db_path.stat().st_ctime,
            "modified": db_path.stat().st_mtime
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Info error: {e}")
