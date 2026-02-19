from typing import Optional

from account.domain.entity.account import Account
from account.domain.entity.account_profile import AccountProfile
from account.domain.value_objects.email import Email
from account.domain.value_objects.login_type import LoginType
from account.repository.account_repository import AccountRepository
from sqlalchemy.orm import Session


class AccountRepositoryImpl(AccountRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def save(self, session: Session, account: Account) -> Account:
        session.add(account)
        return account

    def find_by_id(
            self,
            session: Session,
            account_id: int
    ) -> Optional[Account]:

        return (
            session.query(Account)
            .filter(Account.id == account_id)
            .first()
        )

    def find_by_email_and_login_type(
        self,
        session: Session,
        email: Email,
        login_type: LoginType
    ) -> Optional[Account]:

        return (
            session.query(Account)
            .join(Account.profile)  # Account -> Profile
            .filter(
                Account.login_type == login_type,
                AccountProfile.email == email.value
            )
            .first()
        )
