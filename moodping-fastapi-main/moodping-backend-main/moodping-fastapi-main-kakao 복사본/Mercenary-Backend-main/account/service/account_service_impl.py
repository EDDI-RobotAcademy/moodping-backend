from typing import Optional

from sqlalchemy.orm import Session

from account.domain.entity.account import Account
from account.domain.value_objects.email import Email
from account.domain.value_objects.login_type import LoginType
from account.domain.value_objects.nickname import Nickname
from account.repository.account_repository_impl import AccountRepositoryImpl
from account.service.account_service import AccountService
from config.mysql_config import MySQLConfig


class AccountServiceImpl(AccountService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.account_repository = AccountRepositoryImpl.get_instance()

        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def register(
        self,
        login_type: str,
        email: Email,
        nickname: Nickname
    ) -> Account:

        session: Session = MySQLConfig().get_session()

        try:
            account = Account.create(
                login_type=login_type,
                email=email,
                nickname=nickname
            )

            self.account_repository.save(session, account)

            session.commit()

            # Lazy 로딩 안전 (세션 살아있음)
            _ = account.profile.email

            return account

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def find_by_email_and_login_type(
            self,
            email: Email,
            login_type: LoginType
    ) -> Optional[Account]:

        session = MySQLConfig().get_session()

        try:
            account = self.account_repository.find_by_email_and_login_type(
                session,
                email,
                login_type
            )

            if account and account.profile:
                # Lazy load 트리거
                _ = account.profile.email
                _ = account.profile.nickname

                account.profile.email = Email(account.profile.email)
                account.profile.nickname = Nickname(account.profile.nickname)

            return account

        finally:
            session.close()

    def lookup(self, account_id: int) -> Account:

        session = MySQLConfig().get_session()

        try:
            account = self.account_repository.find_by_id(
                session,
                account_id
            )

            if not account:
                raise ValueError(f"Account not found. id={account_id}")

            # Lazy loading 안전 확보
            if account.profile:
                _ = account.profile.email
                _ = account.profile.nickname

                account.profile.email = Email(account.profile.email)
                account.profile.nickname = Nickname(account.profile.nickname)

            return account

        finally:
            session.close()