# MoodPing FastAPI 백엔드

감정 기록 + AI 분석 웹앱 백엔드 (FastAPI / Python 3.11+)

> Spring Boot 버전은 `moodping-backend/` 폴더를 참고하세요.

## 빠른 시작

### 1. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

### 2. Docker로 MySQL 실행

```bash
docker compose up -d
# Spring Boot 버전과 동시에 사용 시 포트 3307 사용 (docker-compose.yml 참고)
```

### 3. Python 가상환경 & 의존성 설치

```bash
python3.13 -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

브라우저에서 `http://localhost:8000` 접속

API 문서: `http://localhost:8000/docs`

---

## 문서

- [PM 코드구조 학습가이드](docs/PM_코드구조_학습가이드.md) – 비전공자 PM용 폴더/도메인/이벤트 로그 구조 설명
- [토큰 사용량](docs/TOKEN_USAGE.md) – LLM 토큰 사용량 및 설정

---

## LLM 전환 방법

`.env` 파일의 `LLM_PROVIDER` 값만 변경하면 됩니다. 코드 수정 불필요.

```bash
LLM_PROVIDER=openai   # GPT-4.1-mini (기본값)
LLM_PROVIDER=gemini   # Gemini 2.5 Flash
LLM_PROVIDER=claude   # Claude Haiku 4.5
```

---

## API 엔드포인트

| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/mood-records` | 감정 기록 저장 + AI 분석 (통합) |
| POST | `/api/events` | 퍼널 이벤트 로그 저장 |
| POST | `/users/link-data` | anon_id → user_id 연동 |
| GET  | `/api/debug/recent-records` | 최근 기록 10건 |
| GET  | `/api/debug/metrics` | 퍼널 이탈률 + 7일 리텐션 |
| GET  | `/docs` | Swagger UI (자동 생성) |

---

## 패키지 구조

```
app/
├── main.py          # 앱 진입점
├── config.py        # 환경변수 설정 (pydantic-settings)
├── database.py      # SQLAlchemy 세션
├── models.py        # ORM 모델
├── schemas.py       # Pydantic 스키마
├── llm/             # LLM Provider 패턴
│   ├── base.py
│   ├── openai_client.py
│   ├── gemini_client.py
│   ├── claude_client.py
│   └── factory.py
├── prompt/          # 프롬프트 빌더
├── services/        # 비즈니스 로직
├── routers/         # API 엔드포인트
└── static/          # 프론트엔드
```
