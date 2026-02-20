import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.domain.mood.router import router as mood_router
from app.domain.event.router import router as event_router
from app.domain.user.router import router as user_router
from app.domain.auth.router import router as auth_router, kakao_redirect_router
from app.domain.report.router import router as report_router
from app.config import get_settings
from app.database import engine, Base

import app.domain.mood.models  # noqa: F401 - register models with Base
import app.domain.event.models  # noqa: F401
import app.domain.user.models  # noqa: F401
import app.domain.report.models  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("MoodPing FastAPI 시작. LLM_PROVIDER=%s", settings.llm_provider)
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("MoodPing FastAPI 종료.")


app = FastAPI(
    title="MoodPing API",
    description="감정 기록 및 AI 분석 웹앱 백엔드",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(kakao_redirect_router)
app.include_router(mood_router)
app.include_router(event_router)
app.include_router(user_router)
app.include_router(report_router)

if STATIC_DIR.exists():
    app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")
    app.mount("/images", StaticFiles(directory=STATIC_DIR / "images"), name="images")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/record", include_in_schema=False)
def record():
    return FileResponse(STATIC_DIR / "record.html")


@app.get("/record.html", include_in_schema=False)
def record_legacy():
    return FileResponse(STATIC_DIR / "record.html")


@app.get("/report", include_in_schema=False)
def report():
    return FileResponse(STATIC_DIR / "report.html")
