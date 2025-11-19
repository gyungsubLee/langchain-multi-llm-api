# LangChain Multi-LLM FastAPI

FastAPI와 LangChain을 사용하여 여러 LLM 모델을 제공하는 API 서버입니다.
**버전 관리**를 통해 기본 LLM 호출(v1)과 Prompt Template 기능(v2)을 제공합니다.

---

## 📑 목차

- [제공 API](#제공-api)
- [빠른 시작](#빠른-시작)
- [API 사용 예제](#api-사용-예제)
- [환경 변수 설정](#환경-변수-설정)
- [프로젝트 구조](#프로젝트-구조)
- [문제 해결](#문제-해결)

---

## 🚀 제공 API

### **V1 - 기본 LLM 호출**

간단한 프롬프트로 LLM을 직접 호출합니다.

- `POST /v1/gpt` — OpenAI GPT 모델
- `POST /v1/gemini` — Google Gemini 모델
- `POST /v1/claude` — Anthropic Claude 모델

**요청 예시:**
```json
{
  "prompt": "안녕하세요"
}
```

---

### **V2 - Prompt Template**

LangChain의 PromptTemplate과 ChatPromptTemplate을 활용한 고급 기능입니다.

- `POST /v2/prompt-template` — PromptTemplate 사용 예제
- `POST /v2/chat-prompt-template` — ChatPromptTemplate 사용 예제
- `POST /v2/translate` — 번역 전용 엔드포인트

**요청 예시:**
```json
{
  "text": "안녕",
  "target_lang": "영어"
}
```

---

### **V4 - Retrieval & RAG** (신규!)

최신 LangChain으로 마이그레이션된 문서 검색 및 RAG (Retrieval-Augmented Generation) 기능입니다.

- `POST /v4/search` — 벡터 데이터베이스 문서 검색
- `POST /v4/rag` — RAG 기반 질의응답
- `POST /v4/upload-pdf` — PDF 업로드 및 벡터 DB 생성

**검색 요청 예시:**
```json
{
  "query": "소개팅 주선자의 역할",
  "top_k": 3
}
```

**RAG 요청 예시:**
```json
{
  "query": "소개팅에서 주의할 점은?",
  "top_k": 2
}
```

**주요 특징:**
- ✅ 최신 LangChain API 사용 (`invoke()` 메서드)
- ✅ `RecursiveCharacterTextSplitter` 적용
- ✅ `create_retrieval_chain` 최신 방식
- ✅ FAISS 벡터 스토어 + 로컬 영구 저장
- ✅ OpenAI Embeddings
- ✅ 벡터 DB 관리 기능 (생성, 조회, 삭제)

**엔드포인트:**
1. `POST /v4/upload-pdf` - PDF 업로드 및 벡터 DB 생성
2. `POST /v4/search` - 벡터 DB에서 문서 검색
3. `POST /v4/rag` - RAG 기반 질의응답
4. `GET /v4/list-dbs` - 저장된 벡터 DB 목록 조회
5. `GET /v4/db-info/{db_name}` - 특정 벡터 DB 정보
6. `DELETE /v4/delete-db/{db_name}` - 벡터 DB 삭제

---

## 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
cd 09-API

# 가상환경 생성 (Python 3.12 권장)
python3.12 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# Windows의 경우
# venv\Scripts\activate
```

> **중요**: Python 3.13은 일부 패키지 호환성 문제가 있을 수 있습니다. Python 3.11 또는 3.12 사용을 권장합니다.

---

### 2. 패키지 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 필요한 패키지 설치
pip install -r requirements.txt
```

---

### 3. 환경 변수 설정 (선택)

Mock 모드로 테스트하려면 이 단계를 건너뛰어도 됩니다.

실제 API를 사용하려면:

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집하여 API 키 설정
# MOCK=false로 설정하고 API 키 입력
```

---

### 4. 테스트 실행

```bash
# 자동으로 서버 시작/v1 v2 테스트/종료
python run_tests.py
```

**테스트 결과:**
```
============================================================
V1 엔드포인트 테스트 (기본 LLM)
============================================================

-> POST http://127.0.0.1:8000/v1/gpt
   Response (200): {'model': 'gpt-mock', 'content': '[MOCK GPT] 안녕'}

============================================================
V2 엔드포인트 테스트 (Prompt Template)
============================================================

-> POST http://127.0.0.1:8000/v2/translate
   Response (200):
     original: 고마워
     target_lang: 중국어
     translated: [MOCK] Translation of '고마워' to 중국어
```

---

## 📖 API 사용 예제

### V1 - 기본 LLM 호출

**curl:**
```bash
curl -X POST http://127.0.0.1:8000/v1/gpt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "안녕하세요"}'
```

**Python:**
```python
import httpx

client = httpx.Client()
response = client.post(
    "http://127.0.0.1:8000/v1/gpt",
    json={"prompt": "안녕하세요"}
)
print(response.json())
# {'model': 'gpt-mock', 'content': '[MOCK GPT] 안녕하세요'}
```

---

### V2 - Prompt Template

#### 1️⃣ PromptTemplate 사용

```bash
curl -X POST http://127.0.0.1:8000/v2/prompt-template \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕", "target_lang": "영어"}'
```

**응답:**
```json
{
  "template": "'{text}' 이 문장을 {target_lang}로 번역해줘",
  "formatted_prompt": "'안녕' 이 문장을 영어로 번역해줘",
  "content": "[MOCK] '안녕' 이 문장을 영어로 번역해줘"
}
```

---

#### 2️⃣ ChatPromptTemplate 사용

```bash
curl -X POST http://127.0.0.1:8000/v2/chat-prompt-template \
  -H "Content-Type: application/json" \
  -d '{
    "text": "좋은 아침",
    "system_message": "사용자의 질의를 일본어로 번역해라."
  }'
```

**응답:**
```json
{
  "system_message": "사용자의 질의를 일본어로 번역해라.",
  "user_message": "좋은 아침",
  "formatted_prompt": "System: 사용자의 질의를 일본어로 번역해라.\nHuman: 좋은 아침",
  "content": "[MOCK] System: 사용자의 질의를 일본어로 번역해라.\nHuman: 좋은 아침"
}
```

---

#### 3️⃣ 번역 엔드포인트

```bash
curl -X POST http://127.0.0.1:8000/v2/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "고마워", "target_lang": "중국어"}'
```

**응답:**
```json
{
  "original": "고마워",
  "target_lang": "중국어",
  "translated": "[MOCK] Translation of '고마워' to 중국어"
}
```

---

### 🔍 V4 - Retrieval & RAG (로컬 벡터 DB)

**로컬 벡터 DB 생성 및 관리**

#### 1️⃣ PDF 업로드 및 벡터 DB 생성

```bash
# MOCK 모드는 불가능, 실제 API 키 필요
curl -X POST "http://127.0.0.1:8000/v4/upload-pdf?db_name=my_docs" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

**응답:**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "db_name": "my_docs",
  "pages": 15,
  "chunks": 42,
  "method": "RecursiveCharacterTextSplitter",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "saved_to": "vector_db/my_docs"
}
```

**저장 위치:** `vector_db/my_docs/` 디렉토리에 FAISS 인덱스 파일 생성

---

#### 2️⃣ 벡터 DB에서 문서 검색

```bash
curl -X POST http://127.0.0.1:8000/v4/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "소개팅 주선자의 역할",
    "top_k": 3,
    "db_name": "my_docs"
  }'
```

**응답:**
```json
[
  {
    "content": "소개팅 주선자는 양측의 성향을 파악하고...",
    "metadata": {"source": "document.pdf", "page": 3},
    "score": null
  },
  ...
]
```

---

#### 3️⃣ RAG 질의응답

```bash
curl -X POST http://127.0.0.1:8000/v4/rag \
  -H "Content-Type: application/json" \
  -d '{
    "query": "소개팅에서 주의할 점은?",
    "top_k": 2,
    "db_name": "my_docs"
  }'
```

**응답:**
```json
{
  "query": "소개팅에서 주의할 점은?",
  "answer": "문서에 따르면, 소개팅에서는...",
  "source_documents": [
    {
      "content": "...",
      "metadata": {"source": "document.pdf", "page": 5},
      "score": null
    }
  ]
}
```

---

#### 4️⃣ 벡터 DB 목록 조회

```bash
curl http://127.0.0.1:8000/v4/list-dbs
```

**응답:**
```json
{
  "count": 2,
  "databases": [
    {
      "name": "my_docs",
      "path": "vector_db/my_docs",
      "size_bytes": 1048576,
      "created": 1700000000.0,
      "modified": 1700000000.0
    },
    ...
  ]
}
```

---

#### 5️⃣ 벡터 DB 정보 조회

```bash
curl http://127.0.0.1:8000/v4/db-info/my_docs
```

**응답:**
```json
{
  "name": "my_docs",
  "path": "vector_db/my_docs",
  "files": {
    "index.faiss": 524288,
    "index.pkl": 102400
  },
  "total_size_bytes": 626688,
  "total_size_mb": 0.6,
  "created": 1700000000.0,
  "modified": 1700000000.0
}
```

---

#### 6️⃣ 벡터 DB 삭제

```bash
curl -X DELETE http://127.0.0.1:8000/v4/delete-db/my_docs
```

**응답:**
```json
{
  "status": "success",
  "message": "Vector DB 'my_docs' has been deleted",
  "deleted_path": "vector_db/my_docs"
}
```

---

## 🌐 브라우저에서 API 문서 확인

서버 실행 후 브라우저에서 접속:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

Swagger UI에서 각 엔드포인트를 직접 테스트할 수 있습니다!

---

## ⚙️ 환경 변수 설정

### Mock 모드 (기본값)

API 키 없이 테스트 가능:

```bash
# .env 파일
MOCK=true
```

또는 환경변수로 직접 설정:

```bash
export MOCK=true
uvicorn app.main:app --reload
```

---

### 실제 API 사용

`.env` 파일에 API 키 설정:

```bash
MOCK=false
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
OPENAI_MODEL=gpt-4o  # 선택사항, 기본값: gpt-4o
```

---

## 🏗️ 클린 아키텍처 구조

**FastAPI 권장 아키텍처 적용: 계층별 책임 분리**

```
09-API/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 애플리케이션 진입점
│   ├── dependencies.py            # 의존성 주입 (DI Container)
│   │
│   ├── api/                       # 🌐 Presentation Layer (라우터)
│   │   ├── v1/llm.py             # V1 엔드포인트: 기본 LLM
│   │   ├── v2/prompt.py          # V2 엔드포인트: Prompt Template
│   │   └── v4/retrieval.py       # V4 엔드포인트: Retrieval & RAG
│   │
│   ├── core/                      # ⚙️ Core Configuration
│   │   └── config.py             # 전역 설정 관리 (Pydantic Settings)
│   │
│   ├── models/                    # 📋 Data Transfer Objects
│   │   └── schemas.py            # Pydantic 요청/응답 스키마
│   │
│   ├── services/                  # 💼 Business Logic Layer
│   │   └── vector_db_service.py  # 벡터 DB 비즈니스 로직
│   │
│   └── repositories/              # 🗄️ Data Access Layer
│       └── vector_db_repository.py  # FAISS 데이터 접근
│
├── vector_db/                     # 로컬 벡터 DB 저장소 (gitignore)
├── Chapter 7. LangChain/          # LangChain 학습 노트북
├── .env.example                   # 환경 변수 템플릿
├── .gitignore                     # Git 제외 파일 설정
├── requirements.txt               # Python 패키지 목록
├── run_tests.py                   # 자동 테스트 스크립트
└── README.md
```

### 아키텍처 레이어 설명

**1. Presentation Layer (API Router)**
- **책임**: HTTP 요청/응답 처리만 담당
- **파일**: `app/api/v4/retrieval.py`
- **특징**: 비즈니스 로직 없음, 서비스 레이어로 위임

**2. Business Logic Layer (Service)**
- **책임**: 핵심 비즈니스 로직 처리
- **파일**: `app/services/vector_db_service.py`
- **특징**: PDF 처리, RAG 체인 구성, 검색 로직

**3. Data Access Layer (Repository)**
- **책임**: 데이터 저장소(FAISS) 직접 접근
- **파일**: `app/repositories/vector_db_repository.py`
- **특징**: CRUD 연산, FAISS API 추상화

**4. Configuration Layer**
- **책임**: 환경 변수 및 설정 관리
- **파일**: `app/core/config.py`
- **특징**: Pydantic Settings, 타입 안전성

**5. Dependency Injection**
- **책임**: 계층 간 의존성 관리
- **파일**: `app/dependencies.py`
- **특징**: FastAPI Depends를 통한 DI 구현

### 설계 원칙

- ✅ **단일 책임 원칙 (SRP)**: 각 레이어는 하나의 책임만
- ✅ **의존성 역전 (DIP)**: 추상화에 의존, 구체 구현에 의존하지 않음
- ✅ **테스트 용이성**: 각 레이어를 독립적으로 테스트 가능
- ✅ **확장성**: 새로운 기능 추가 시 레이어별로 확장
- ✅ **유지보수성**: 변경 영향 최소화, 코드 가독성 향상

---

## 🛠️ VSCode에서 가상환경 사용

1. VSCode에서 `Cmd+Shift+P` (Windows: `Ctrl+Shift+P`)
2. "Python: Select Interpreter" 선택
3. `./venv/bin/python` 선택
4. 터미널 재시작하면 자동으로 가상환경 활성화

---

## 🔧 수동 서버 실행

```bash
# Mock 모드로 실행 (API 키 불필요)
MOCK=true uvicorn app.main:app --reload

# 실제 API 사용 (API 키 필요)
uvicorn app.main:app --reload

# 다른 포트로 실행
uvicorn app.main:app --reload --port 8001
```

---

## ❓ 문제 해결

### Python 버전 문제

Python 3.13에서 `tiktoken` 빌드 오류가 발생할 수 있습니다.

**해결 방법**: Python 3.12 또는 3.11 사용

```bash
# 기존 가상환경 삭제
deactivate
rm -rf venv

# Python 3.12로 가상환경 재생성
python3.12 -m venv venv
source venv/bin/activate

# 패키지 재설치
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 포트 8000이 이미 사용 중인 경우

다른 포트로 서버 실행:

```bash
uvicorn app.main:app --reload --port 8001
```

---

### API 키 오류

- `.env` 파일이 올바른 위치에 있는지 확인
- API 키가 정확한지 확인
- `MOCK=true`로 설정하여 API 키 없이 테스트

---

### 패키지 설치 오류

가상환경이 활성화되어 있는지 확인:

```bash
which python
# 출력: /Users/.../09-API/venv/bin/python
```

---

## 🔗 관련 링크

- **GitHub 저장소**: https://github.com/gyungsubLee/langchain-multi-llm-api
- **LangChain 공식 문서**: https://python.langchain.com/
- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/

---

## 📝 버전 관리

### v4.0.0 (현재)
- ✅ v4: Retrieval & RAG 기능 추가
- ✅ 최신 LangChain API로 마이그레이션
  - `invoke()` 메서드 사용
  - `RecursiveCharacterTextSplitter` 적용
  - `create_retrieval_chain` 최신 방식
- ✅ FAISS 벡터 스토어 지원
- ✅ PDF 업로드 및 벡터 DB 생성 기능

### v2.0.0
- ✅ API 버전 관리 시스템 도입
- ✅ v1: 기본 LLM 호출 엔드포인트
- ✅ v2: Prompt Template 기능 추가
- ✅ 파일별 엔드포인트 분리 구조

### v1.0.0
- ✅ 기본 GPT/Gemini/Claude 엔드포인트
- ✅ Mock 모드 지원
- ✅ 자동 테스트 스크립트

---

## 🤝 Contributing

이슈나 개선 사항이 있으면 GitHub Issues에 등록해주세요!

---

## 📄 License

MIT License
