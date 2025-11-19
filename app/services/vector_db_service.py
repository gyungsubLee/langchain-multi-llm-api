"""
벡터 DB 비즈니스 로직 레이어
"""
from typing import List
import tempfile
import os
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from app.repositories.vector_db_repository import VectorDBRepository
from app.models.schemas import (
    DocumentResponse,
    RAGResponse,
    UploadResponse,
    VectorDBListResponse,
    VectorDBDetailResponse,
    DeleteResponse
)
from app.core.config import settings


class VectorDBService:
    """벡터 DB 비즈니스 로직"""

    def __init__(self, repository: VectorDBRepository):
        self.repository = repository

    async def upload_pdf(
        self,
        file: UploadFile,
        db_name: str = "default"
    ) -> UploadResponse:
        """PDF 업로드 및 벡터 DB 생성"""
        tmp_path = None
        try:
            # 임시 파일 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name

            # PDF 로드
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()

            # 텍스트 분할
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                separators=settings.TEXT_SPLITTER_SEPARATORS
            )
            chunks = text_splitter.split_documents(pages)

            # 벡터 DB 생성 및 저장
            self.repository.create_db_from_documents(chunks, db_name)

            return UploadResponse(
                status="success",
                filename=file.filename,
                db_name=db_name,
                pages=len(pages),
                chunks=len(chunks),
                method="RecursiveCharacterTextSplitter",
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                saved_to=str(self.repository.get_db_path(db_name))
            )

        finally:
            # 임시 파일 정리
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def search_documents(
        self,
        query: str,
        top_k: int = 3,
        db_name: str = "default"
    ) -> List[DocumentResponse]:
        """벡터 DB에서 문서 검색"""
        # DB 로드
        db = self.repository.load_db(db_name)
        retriever = db.as_retriever(search_kwargs={"k": top_k})

        # 검색 실행
        docs = retriever.invoke(query)

        return [
            DocumentResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                score=None
            )
            for doc in docs
        ]

    def rag_query(
        self,
        query: str,
        top_k: int = 3,
        db_name: str = "default"
    ) -> RAGResponse:
        """RAG 기반 질의응답"""
        # DB 로드
        db = self.repository.load_db(db_name)
        retriever = db.as_retriever(search_kwargs={"k": top_k})

        # LLM 설정
        llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)

        # 프롬프트 템플릿
        system_prompt = """다음 문서를 참고하여 질문에 답변하세요.

        {context}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

        # RAG Chain 생성
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # 실행
        result = rag_chain.invoke({"input": query})

        # 응답 생성
        source_docs = [
            DocumentResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                score=None
            )
            for doc in result.get("context", [])
        ]

        return RAGResponse(
            query=query,
            answer=result["answer"],
            source_documents=source_docs
        )

    def list_databases(self) -> VectorDBListResponse:
        """모든 벡터 DB 목록 조회"""
        dbs = self.repository.list_dbs()
        return VectorDBListResponse(
            count=len(dbs),
            databases=dbs
        )

    def get_database_info(self, db_name: str) -> VectorDBDetailResponse:
        """특정 벡터 DB 정보 조회"""
        info = self.repository.get_db_info(db_name)
        return VectorDBDetailResponse(**info)

    def delete_database(self, db_name: str) -> DeleteResponse:
        """벡터 DB 삭제"""
        deleted_path = self.repository.delete_db(db_name)
        return DeleteResponse(
            status="success",
            message=f"Vector DB '{db_name}' has been deleted",
            deleted_path=str(deleted_path)
        )
