import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.routers import mood_records, events, users, debug, auth
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("MoodPing FastAPI 시작. LLM_PROVIDER=%s", settings.llm_provider)
    yield
    logger.info("MoodPing FastAPI 종료.")


app = FastAPI(
    title="MoodPing API",
    description="감정 기록 및 AI 분석 웹앱 백엔드",
    version="1.0.0",
    lifespan=lifespan,
)

# API 라우터 등록
app.include_router(mood_records.router)
app.include_router(events.router)
app.include_router(users.router)
app.include_router(debug.router)
app.include_router(auth.router)

# 정적 파일 서빙 (CSS, JS)
if STATIC_DIR.exists():
    app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")


# HTML 페이지 라우팅
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/record.html", include_in_schema=False)
def record():
    return FileResponse(STATIC_DIR / "record.html")
