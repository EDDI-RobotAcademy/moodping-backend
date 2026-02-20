from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class MySQLConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        user = os.getenv("MYSQL_USER")
        password = urllib.parse.quote_plus(os.getenv("MYSQL_PASSWORD", ""))
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT")
        db = os.getenv("MYSQL_DB")

        self._url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
        self._engine = create_engine(self._url, echo=True, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False, bind=self._engine)
        self.Base = declarative_base()

    def get_engine(self):
        return self._engine

    def get_session(self):
        return self.SessionLocal()

    def get_base(self):
        return self.Base
