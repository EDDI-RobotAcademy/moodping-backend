from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from account.controller.account_controller import account_router
from authentication.controller.authentication_controller import authentication_router
from board.controller.board_controller import board_router

from config.mysql_config import MySQLConfig
from config.settings import get_settings
from kakao_authentication.controller.kakao_authentication_controller import kakao_authentication_router

settings = get_settings()

app = FastAPI(
    title="FastAPI Backend",
    description="FastAPI 백엔드 프로젝트",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kakao_authentication_router)
app.include_router(account_router)
app.include_router(board_router)
app.include_router(authentication_router)

if __name__ == "__main__":
    import uvicorn

    Base = MySQLConfig().get_base()
    engine = MySQLConfig().get_engine()

    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    uvicorn.run(app, host="0.0.0.0", port=33333)
