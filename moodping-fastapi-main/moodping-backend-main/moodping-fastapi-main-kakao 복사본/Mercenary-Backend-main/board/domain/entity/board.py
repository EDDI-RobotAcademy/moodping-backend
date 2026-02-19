from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from config.mysql_config import MySQLConfig

Base = MySQLConfig().get_base()


class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(200), nullable=False)
    content = Column(String(5000), nullable=False)

    account_id = Column(
        Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 추가

    account = relationship("Account", lazy="select")

    @classmethod
    def create(cls, account_id: int, title: str, content: str):

        if not title or not title.strip():
            raise ValueError("Title must not be empty")

        if not content or not content.strip():
            raise ValueError("Content must not be empty")

        if len(title) > 200:
            raise ValueError("Title too long")

        return cls(
            account_id=account_id,
            title=title.strip(),
            content=content.strip()
        )
