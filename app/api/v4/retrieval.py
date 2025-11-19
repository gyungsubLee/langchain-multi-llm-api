"""
API v4 - Retrieval & RAG Endpoints
최신 LangChain으로 마이그레이션된 문서 검색 및 RAG 기능
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile

router = APIRouter(prefix="/v4", tags=["v4-retrieval-rag"])


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


class DocumentResponse(BaseModel):
    content: str
    metadata: dict
    score: Optional[float] = None


class RAGRequest(BaseModel):
    query: str
    top_k: int = 3


class RAGResponse(BaseModel):
    query: str
    answer: str
    source_documents: List[DocumentResponse]


MOCK = os.getenv("MOCK", "true").lower() == "true"


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
        # 최신 LangChain imports
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain_community.document_loaders import PyPDFLoader
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing packages: {e}")

    # TODO: 실제 구현에서는 미리 생성된 벡터 DB를 로드
    # 여기서는 간단한 예제로 처리
    try:
        # 임시 문서 로드 (실제로는 사전에 구축된 벡터 DB 사용)
        embeddings = OpenAIEmbeddings()

        # 예제: 간단한 in-memory 벡터 DB
        from langchain.schema import Document
        sample_docs = [
            Document(page_content=f"샘플 문서 {i}", metadata={"source": f"doc_{i}.txt"})
            for i in range(5)
        ]

        db = FAISS.from_documents(sample_docs, embeddings)
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
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.chains import RetrievalQA
        from langchain.schema import Document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing packages: {e}")

    try:
        # 임시 벡터 DB 생성 (실제로는 사전 구축된 DB 사용)
        embeddings = OpenAIEmbeddings()
        sample_docs = [
            Document(page_content=f"샘플 지식: {req.query}에 대한 내용 {i}", metadata={"source": f"kb_{i}.txt"})
            for i in range(req.top_k)
        ]

        db = FAISS.from_documents(sample_docs, embeddings)
        retriever = db.as_retriever(search_kwargs={"k": req.top_k})

        # LLM 설정
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        llm = ChatOpenAI(model=model_name, temperature=0)

        # 최신 방식: create_retrieval_chain 사용
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains import create_retrieval_chain
        from langchain_core.prompts import ChatPromptTemplate

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {e}")


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    PDF 파일 업로드 및 벡터 DB 생성
    (최신 RecursiveCharacterTextSplitter 사용)
    """
    if MOCK:
        return {
            "status": "success",
            "filename": file.filename,
            "message": "[MOCK] PDF가 업로드되고 벡터 DB에 추가되었습니다.",
            "chunks": 42,
            "method": "RecursiveCharacterTextSplitter"
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

        # TODO: 실제로는 DB를 디스크에 저장
        # db.save_local("vectorstore/")

        # 임시 파일 삭제
        os.unlink(tmp_path)

        return {
            "status": "success",
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "method": "RecursiveCharacterTextSplitter",
            "chunk_size": 1000,
            "chunk_overlap": 200
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")
