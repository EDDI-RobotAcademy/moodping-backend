from sqlalchemy import BigInteger, Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "user"

    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    kakao_id      = Column(String(100), nullable=False, unique=True)
    nickname      = Column(String(100), nullable=True)
    profile_image = Column(String(500), nullable=True)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())
    updated_at    = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
