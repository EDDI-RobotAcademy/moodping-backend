from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.mysql_config import MySQLConfig

Base = MySQLConfig().get_base()


class AccountProfile(Base):
    __tablename__ = "account_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)

    account_id = Column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
        unique=True
    )

    email = Column(String(255), nullable=False, unique=True)
    nickname = Column(String(100), nullable=False)

    account = relationship("Account", back_populates="profile")
