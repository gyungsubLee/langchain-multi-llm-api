# FastAPI Clean Architecture Rules

## 개요
FastAPI 프로젝트 생성 및 리팩토링 시 자동으로 적용되는 아키텍처 규칙

## 디렉토리 구조

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 애플리케이션 진입점
│   ├── dependencies.py          # 의존성 주입 컨테이너
│   │
│   ├── api/                     # Presentation Layer
│   │   └── v{version}/
│   │       ├── __init__.py
│   │       └── {resource}.py    # 라우터 (HTTP 처리만)
│   │
│   ├── core/                    # Core Configuration
│   │   ├── __init__.py
│   │   └── config.py           # Pydantic Settings
│   │
│   ├── models/                  # Data Transfer Objects
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic 스키마
│   │
│   ├── services/                # Business Logic Layer
│   │   ├── __init__.py
│   │   └── {resource}_service.py
│   │
│   └── repositories/            # Data Access Layer
│       ├── __init__.py
│       └── {resource}_repository.py
│
├── tests/                       # 테스트 (구조 동일)
├── .env.example                 # 환경 변수 템플릿
├── requirements.txt
└── README.md
```

## 레이어별 책임

### 1. Presentation Layer (Router)
**파일 위치**: `app/api/v{version}/{resource}.py`

**책임**:
- HTTP 요청/응답 처리만
- 요청 검증 (Pydantic)
- 서비스 레이어 호출
- HTTP 상태 코드 반환

**금지 사항**:
- ❌ 비즈니스 로직 작성
- ❌ 데이터베이스 직접 접근
- ❌ 외부 API 직접 호출
- ❌ 하드코딩된 값 사용

**코드 템플릿**:
```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import RequestSchema, ResponseSchema
from app.services.resource_service import ResourceService
from app.dependencies import get_resource_service

router = APIRouter(prefix="/v1/{resource}", tags=["v1-{resource}"])

@router.post("/", response_model=ResponseSchema)
async def create_resource(
    req: RequestSchema,
    service: ResourceService = Depends(get_resource_service)
):
    """리소스 생성"""
    try:
        return await service.create(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 2. Business Logic Layer (Service)
**파일 위치**: `app/services/{resource}_service.py`

**책임**:
- 핵심 비즈니스 로직 구현
- 여러 Repository 조율
- 외부 서비스 호출 (LLM, API 등)
- 데이터 변환 및 검증

**금지 사항**:
- ❌ HTTP 관련 코드 (Request, Response 등)
- ❌ 데이터베이스 직접 접근 (Repository 사용)
- ❌ 하드코딩된 설정값

**코드 템플릿**:
```python
from typing import List
from app.repositories.resource_repository import ResourceRepository
from app.models.schemas import RequestSchema, ResponseSchema
from app.core.config import settings

class ResourceService:
    """리소스 비즈니스 로직"""

    def __init__(self, repository: ResourceRepository):
        self.repository = repository

    async def create(self, req: RequestSchema) -> ResponseSchema:
        """리소스 생성 비즈니스 로직"""
        # 1. 비즈니스 규칙 검증
        self._validate_business_rules(req)

        # 2. 데이터 변환
        data = self._transform_data(req)

        # 3. Repository 호출
        result = await self.repository.create(data)

        # 4. 응답 생성
        return ResponseSchema(**result)

    def _validate_business_rules(self, req: RequestSchema):
        """비즈니스 규칙 검증 (private)"""
        if req.value < settings.MIN_VALUE:
            raise ValueError(f"Value must be >= {settings.MIN_VALUE}")
```

---

### 3. Data Access Layer (Repository)
**파일 위치**: `app/repositories/{resource}_repository.py`

**책임**:
- 데이터 저장소 직접 접근 (DB, File, API 등)
- CRUD 연산
- 데이터 저장소 API 추상화

**금지 사항**:
- ❌ 비즈니스 로직
- ❌ HTTP 처리
- ❌ 복잡한 데이터 변환

**코드 템플릿**:
```python
from pathlib import Path
from typing import List, Optional

class ResourceRepository:
    """리소스 데이터 접근"""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    async def create(self, data: dict) -> dict:
        """데이터 생성"""
        # 데이터 저장소에 저장
        return data

    async def get_by_id(self, id: str) -> Optional[dict]:
        """ID로 조회"""
        # 데이터 저장소에서 조회
        return None

    async def list(self, skip: int = 0, limit: int = 10) -> List[dict]:
        """목록 조회"""
        # 데이터 저장소에서 목록 조회
        return []

    async def update(self, id: str, data: dict) -> dict:
        """데이터 수정"""
        # 데이터 저장소에서 수정
        return data

    async def delete(self, id: str) -> bool:
        """데이터 삭제"""
        # 데이터 저장소에서 삭제
        return True
```

---

### 4. Configuration Layer
**파일 위치**: `app/core/config.py`

**책임**:
- 환경 변수 관리
- 애플리케이션 설정
- 타입 안전한 설정 제공

**코드 템플릿**:
```python
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    # API 설정
    API_TITLE: str = "My API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 외부 서비스
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    # 데이터베이스/스토리지
    STORAGE_PATH: Path = Path("storage")

    # 비즈니스 로직 설정
    MIN_VALUE: int = 0
    MAX_VALUE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# 싱글톤 인스턴스
settings = Settings()

# 초기화 로직
settings.STORAGE_PATH.mkdir(exist_ok=True)
```

---

### 5. Data Transfer Objects (DTOs)
**파일 위치**: `app/models/schemas.py`

**책임**:
- API 요청/응답 스키마 정의
- 데이터 검증
- API 문서 생성

**코드 템플릿**:
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# === 요청 스키마 ===

class CreateRequest(BaseModel):
    """생성 요청"""
    name: str = Field(..., min_length=1, max_length=100, description="이름")
    value: int = Field(..., ge=0, le=100, description="값 (0-100)")
    tags: List[str] = Field(default=[], description="태그 목록")

class UpdateRequest(BaseModel):
    """수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    value: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None

# === 응답 스키마 ===

class ResourceResponse(BaseModel):
    """리소스 응답"""
    id: str = Field(..., description="리소스 ID")
    name: str = Field(..., description="이름")
    value: int = Field(..., description="값")
    tags: List[str] = Field(..., description="태그 목록")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

class ListResponse(BaseModel):
    """목록 응답"""
    total: int = Field(..., description="전체 개수")
    items: List[ResourceResponse] = Field(..., description="리소스 목록")
```

---

### 6. Dependency Injection
**파일 위치**: `app/dependencies.py`

**책임**:
- 레이어 간 의존성 관리
- 객체 생성 및 주입

**코드 템플릿**:
```python
from fastapi import Depends
from app.core.config import settings
from app.repositories.resource_repository import ResourceRepository
from app.services.resource_service import ResourceService

def get_resource_repository() -> ResourceRepository:
    """Repository 의존성"""
    return ResourceRepository(storage_path=settings.STORAGE_PATH)

def get_resource_service(
    repository: ResourceRepository = Depends(get_resource_repository)
) -> ResourceService:
    """Service 의존성"""
    return ResourceService(repository=repository)
```

---

## 설계 원칙

### SOLID 원칙
1. **단일 책임 원칙 (SRP)**: 각 클래스는 하나의 책임만
2. **개방-폐쇄 원칙 (OCP)**: 확장에는 열려있고 수정에는 닫혀있음
3. **리스코프 치환 원칙 (LSP)**: 추상화 타입으로 치환 가능
4. **인터페이스 분리 원칙 (ISP)**: 필요한 인터페이스만 의존
5. **의존성 역전 원칙 (DIP)**: 추상화에 의존, 구체화에 비의존

### 추가 원칙
- **DRY (Don't Repeat Yourself)**: 중복 제거
- **KISS (Keep It Simple, Stupid)**: 단순함 유지
- **YAGNI (You Aren't Gonna Need It)**: 필요한 것만 구현

---

## 네이밍 컨벤션

### 파일명
- 소문자 + 언더스코어: `user_service.py`, `vector_db_repository.py`
- 복수형 디렉토리: `services/`, `repositories/`, `models/`

### 클래스명
- PascalCase: `UserService`, `VectorDBRepository`
- 접미사 사용: `{Resource}Service`, `{Resource}Repository`

### 함수명
- snake_case: `get_user()`, `create_resource()`
- 동사로 시작: `create_`, `get_`, `update_`, `delete_`, `list_`

### 변수명
- snake_case: `user_id`, `total_count`
- 명확한 의미: `req` (X) → `request` (O)

---

## 리팩토링 체크리스트

기존 코드를 클린 아키텍처로 리팩토링할 때:

- [ ] 하드코딩된 값 → `config.py`로 이동
- [ ] 라우터에서 비즈니스 로직 → Service로 이동
- [ ] Service에서 데이터 접근 → Repository로 이동
- [ ] 중복된 스키마 → `schemas.py`로 통합
- [ ] 의존성 직접 생성 → `dependencies.py`로 이동
- [ ] 타입 힌트 추가 (모든 함수/메서드)
- [ ] Docstring 추가 (public 메서드)
- [ ] 예외 처리 추가 (각 레이어별)
- [ ] 테스트 코드 작성 (각 레이어별)

---

## 자동 적용 규칙

Claude가 FastAPI 코드 작성 시 자동으로:

1. ✅ 5계층 구조로 파일 분리
2. ✅ 각 레이어에 맞는 책임만 부여
3. ✅ Pydantic Settings로 설정 관리
4. ✅ FastAPI Depends로 의존성 주입
5. ✅ 타입 힌트 및 Docstring 추가
6. ✅ 예외 처리 및 에러 메시지
7. ✅ 테스트 가능한 구조 설계
