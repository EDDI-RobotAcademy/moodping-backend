# MoodPing 코드 구조 학습 가이드 (비전공자 PM용)

> 이 문서는 비전공자 PM이 서비스 코드 구조를 이해하고, 바이브 코딩 시 폴더·도메인·이벤트 로그 설계를 빠르게 파악할 수 있도록 작성되었습니다.
포함 내용
폴더 구조 개요
도메인 분리 체계 (auth, user, mood, event, report)
도메인별 파일 역할 (router, service, models, schemas)
이벤트 로그 설계 (퍼널 단계, 저장 구조, 프론트 연결)
PM용 체크리스트 (폴더·도메인·이벤트 로그 확인)
학습 활용 팁 (처음 볼 때, 기능별로 볼 때, 바이브 코딩할 때)
요약 다이어그램
API 엔드포인트 매핑표

---

## 1. 이 프로젝트는 어떤 서비스인가?

**MoodPing**은 감정 기록 + AI 분석 웹앱입니다.

- 사용자가 감정(이모지, 강도, 메모)을 기록
- AI가 기록을 분석해 피드백 제공
- 주간 리포트 생성
- 카카오 로그인 지원
- 퍼널·리텐션 분석용 이벤트 로그 수집

---

## 2. 폴더 구조 한눈에 보기

```
moodping-fastapi-main-kakao/
│
├── app/                          ← 애플리케이션 코드의 중심
│   ├── main.py                   ← 앱 진입점 (라우터 등록, 서버 시작)
│   ├── config.py                 ← 환경변수 설정
│   ├── database.py               ← DB 연결
│   ├── deps.py                   ← 공통 의존성 (예: 로그인 사용자 조회)
│   │
│   ├── domain/                   ← ★ 도메인 단위로 분리된 핵심 영역
│   │   ├── auth/                 ← 인증 (카카오 로그인, JWT)
│   │   ├── user/                 ← 사용자 (anon→user 연동)
│   │   ├── mood/                 ← 감정 기록 + AI 분석
│   │   ├── event/                ← 이벤트 로그 + 퍼널/리텐션
│   │   └── report/               ← 주간 리포트
│   │
│   ├── llm/                      ← AI(LLM) 연동 (OpenAI, Gemini, Claude)
│   ├── prompt/                   ← AI에게 보내는 프롬프트 템플릿
│   └── static/                   ← 프론트엔드 (HTML, CSS, JS)
│
├── schema.sql                    ← DB 테이블 정의
├── requirements.txt              ← Python 패키지 목록
└── .env.example                  ← 환경변수 예시
```

---

## 3. 도메인 분리 체계

### 3.1 도메인 단위로 나뉘어 있는가?

**네.** `app/domain/` 아래가 **도메인 단위**로 나뉘어 있습니다.

| 도메인 | 역할 | 책임 |
|--------|------|------|
| **auth** | 인증 | 카카오 로그인, JWT 발급, 로그인 사용자 정보 제공 |
| **user** | 사용자 | 익명 사용자(anon_id)와 로그인 사용자(user_id) 연동 |
| **mood** | 감정 기록 | 감정 저장, AI 분석 호출, anon→user 연동 처리 |
| **event** | 이벤트 로그 | 퍼널 이벤트 저장, 퍼널/리텐션 지표 계산 |
| **report** | 리포트 | 주간 리포트 생성·조회 |

### 3.2 각 도메인 폴더 안의 구조

도메인마다 **역할별 파일**이 있습니다.

| 파일 | 역할 | 비유 |
|------|------|------|
| **router.py** | API 엔드포인트 정의 | "손님 접대" – 요청을 받고 응답을 돌려줌 |
| **service.py** | 비즈니스 로직 | "실제 일 처리" – 저장, 계산, 외부 호출 등 |
| **models.py** | DB 테이블 구조 | "저장소 설계" – 어떤 컬럼으로 저장할지 |
| **schemas.py** | 요청/응답 형식 | "입출력 규격" – API로 주고받는 데이터 형식 |

예: `domain/mood/`  
- `router.py` → `/mood-records` POST 요청 수신  
- `service.py` → DB 저장 + AI 분석 호출  
- `models.py` → `mood_record`, `mood_analysis` 테이블  
- `schemas.py` → `MoodRecordRequest`, `MoodRecordResponse` 정의  

---

## 4. 이벤트 로그 설계

### 4.1 이벤트 로그의 목적

- **퍼널 분석**: 기록 화면 진입 → 이모지 선택 → 강도 선택 → … → 분석 조회까지 단계별 이탈률
- **리텐션**: 첫 분석 조회 후 7일 내 재방문 비율

### 4.2 이벤트 흐름 (퍼널 단계)

```
record_screen_view    → 페이지 진입
emoji_selected       → 이모지 선택
intensity_selected   → 강도 선택
text_input_start     → 텍스트 입력 시작
record_complete      → 기록 완료
analysis_view        → 분석 조회
feedback_confirmed   → 확인 완료
```

### 4.3 이벤트 로그 저장 구조

| 필드 | 설명 |
|------|------|
| `event_id` | 프론트에서 생성한 고유 ID (중복 방지) |
| `session_id` | 세션 단위 퍼널 추적 |
| `user_id` / `anon_id` | 로그인/비로그인 사용자 식별 |
| `event_name` | 위 7단계 중 하나 |
| `occurred_at` | 발생 시각 |
| `extra_data` | 추가 데이터 (예: 선택한 이모지, 강도 등) |

### 4.4 프론트엔드와의 연결

`app/static/js/record.js`에서 예를 들면:

- `logEvent('record_screen_view')` – 페이지 진입 시
- `logEvent('emoji_selected', {label: recordData.moodLabel})` – 이모지 선택 시
- `logEvent('intensity_selected', {intensity: recordData.intensity})` – 강도 선택 시
- `logEvent('text_input_start')` – 메모 입력 시작 시
- `record_complete` – 기록 완료 시

이 호출들이 `/api/events`로 전송되고, `domain/event/service.py`에서 DB에 저장됩니다.

---

## 5. PM이 코드/바이브 코딩할 때 보면 좋은 체크리스트

### 5.1 폴더 구조 파악

1. **도메인 폴더**가 있는지 확인 (`domain/`, `modules/` 등)
2. **도메인 이름**이 비즈니스 용어인지 확인 (auth, mood, event 등)
3. **도메인별 파일 패턴** 확인: router, service, models, schemas 등

### 5.2 도메인 역할 파악

1. **router** → 어떤 API가 있는지 (`/mood-records`, `/api/events` 등)
2. **service** → 핵심 비즈니스 로직이 어디에 있는지
3. **models** → 어떤 테이블/엔티티가 있는지
4. **schemas** → API 요청/응답 형식

### 5.3 이벤트 로그 설계 확인

1. **이벤트 이름**이 퍼널 단계와 맞는지
2. **session_id**로 세션 단위 추적이 되는지
3. **user_id / anon_id**로 사용자 식별이 되는지
4. **extra_data**로 필요한 추가 정보가 들어가는지

### 5.4 의존성 흐름

- `main.py` → 각 도메인 `router` 등록
- `router` → `service` 호출
- `service` → `models` 사용, `llm`, `prompt` 등 활용

---

## 6. 학습 자료 활용 팁

### 6.1 처음 볼 때

1. **README.md** → 서비스 개요, 실행 방법
2. **schema.sql** → 어떤 데이터를 다루는지
3. **app/main.py** → 어떤 도메인(라우터)이 등록되어 있는지
4. **app/domain/** → 도메인별 역할과 책임

### 6.2 기능별로 볼 때

- "감정 기록" → `domain/mood/`
- "로그인" → `domain/auth/`
- "퍼널/리텐션" → `domain/event/`
- "주간 리포트" → `domain/report/`

### 6.3 바이브 코딩할 때

- "이 API를 추가하려면" → 해당 도메인 `router` + `service` + `schemas` 확인
- "이벤트를 추가하려면" → `domain/event/` + 프론트 `logEvent()` 호출 위치 확인
- "새 도메인이 필요하면" → `domain/` 아래 새 폴더 + router, service, models, schemas 패턴 참고

---

## 7. 요약 다이어그램

```
[사용자 요청]
      ↓
  main.py (라우터 등록)
      ↓
  domain/xxx/router.py (엔드포인트)
      ↓
  domain/xxx/service.py (비즈니스 로직)
      ↓
  domain/xxx/models.py (DB)  또는  llm/ (AI)
      ↓
  [응답 반환]
```

---

## 8. API 엔드포인트 매핑

| 메서드 | URL | 도메인 | 설명 |
|--------|-----|--------|------|
| POST | `/mood-records` | mood | 감정 기록 저장 + AI 분석 |
| POST | `/api/events` | event | 퍼널 이벤트 로그 저장 |
| POST | `/users/link-data` | user | anon_id → user_id 연동 |
| GET | `/api/reports/weekly/latest` | report | 주간 리포트 조회 |
| GET | `/auth/kakao` | auth | 카카오 로그인 시작 |
| GET | `/auth/me` | auth | 로그인 사용자 정보 |
| GET | `/api/debug/recent-records` | event | 최근 기록 10건 |
| GET | `/api/debug/metrics` | event | 퍼널 이탈률 + 7일 리텐션 |

---

*이 문서는 프로젝트 구조 변경 시 함께 업데이트하는 것을 권장합니다.*
