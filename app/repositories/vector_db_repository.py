"""
벡터 DB 데이터 접근 레이어
FAISS와의 직접적인 상호작용 담당
"""
from pathlib import Path
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document


class VectorDBRepository:
    """벡터 DB 저장소 관리"""

    def __init__(self, vector_db_dir: Path):
        self.vector_db_dir = vector_db_dir
        self.embeddings = None

    def _get_embeddings(self) -> OpenAIEmbeddings:
        """임베딩 모델 초기화 (지연 로딩)"""
        if self.embeddings is None:
            self.embeddings = OpenAIEmbeddings()
        return self.embeddings

    def db_exists(self, db_name: str) -> bool:
        """벡터 DB 존재 여부 확인"""
        db_path = self.vector_db_dir / db_name
        index_file = db_path / "index.faiss"
        return db_path.exists() and index_file.exists()

    def get_db_path(self, db_name: str) -> Path:
        """벡터 DB 경로 반환"""
        return self.vector_db_dir / db_name

    def load_db(self, db_name: str) -> FAISS:
        """벡터 DB 로드"""
        if not self.db_exists(db_name):
            raise FileNotFoundError(f"Vector DB '{db_name}' not found")

        db_path = self.get_db_path(db_name)
        embeddings = self._get_embeddings()

        return FAISS.load_local(
            str(db_path),
            embeddings,
            allow_dangerous_deserialization=True
        )

    def save_db(self, db: FAISS, db_name: str) -> Path:
        """벡터 DB 저장"""
        db_path = self.get_db_path(db_name)
        db.save_local(str(db_path))
        return db_path

    def create_db_from_documents(
        self,
        documents: List[Document],
        db_name: str
    ) -> FAISS:
        """문서로부터 벡터 DB 생성"""
        embeddings = self._get_embeddings()
        db = FAISS.from_documents(documents, embeddings)
        self.save_db(db, db_name)
        return db

    def delete_db(self, db_name: str) -> Path:
        """벡터 DB 삭제"""
        import shutil

        db_path = self.get_db_path(db_name)
        if not db_path.exists():
            raise FileNotFoundError(f"Vector DB '{db_name}' not found")

        shutil.rmtree(db_path)
        return db_path

    def list_dbs(self) -> List[dict]:
        """모든 벡터 DB 목록 조회"""
        dbs = []
        for db_path in self.vector_db_dir.iterdir():
            if db_path.is_dir():
                index_file = db_path / "index.faiss"
                if index_file.exists():
                    db_info = {
                        "name": db_path.name,
                        "path": str(db_path),
                        "size_bytes": sum(
                            f.stat().st_size
                            for f in db_path.rglob('*')
                            if f.is_file()
                        ),
                        "created": db_path.stat().st_ctime,
                        "modified": db_path.stat().st_mtime
                    }
                    dbs.append(db_info)
        return dbs

    def get_db_info(self, db_name: str) -> dict:
        """특정 벡터 DB 상세 정보"""
        db_path = self.get_db_path(db_name)

        if not db_path.exists():
            raise FileNotFoundError(f"Vector DB '{db_name}' not found")

        index_file = db_path / "index.faiss"
        pkl_file = db_path / "index.pkl"

        if not index_file.exists():
            raise ValueError(f"Invalid vector DB: missing index.faiss")

        total_size = sum(
            f.stat().st_size
            for f in db_path.rglob('*')
            if f.is_file()
        )

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
