from sqlalchemy import Column, Integer, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from account.domain.entity.account_profile import AccountProfile
from account.domain.value_objects.login_type import LoginType
from config.mysql_config import MySQLConfig

Base = MySQLConfig().get_base()


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, autoincrement=True)

    login_type = Column(
        Enum(LoginType, name="login_type_enum"),
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship(
        "AccountProfile",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select"
    )

    @classmethod
    def create(cls, login_type: str, email: str, nickname: str):

        try:
            login_enum = LoginType(login_type)

        except ValueError:
            raise ValueError("Invalid login type")

        account = cls(login_type=login_enum)

        account.profile = AccountProfile(
            email=email,
            nickname=nickname
        )

        return account
