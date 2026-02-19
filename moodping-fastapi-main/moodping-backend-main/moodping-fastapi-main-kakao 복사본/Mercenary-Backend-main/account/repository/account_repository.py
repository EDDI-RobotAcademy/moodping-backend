from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session

from account.domain.entity.account import Account
from account.domain.value_objects.login_type import LoginType


class AccountRepository(ABC):

    @abstractmethod
    def save(self, session: Session, account: Account) -> Account:
        pass

    @abstractmethod
    def find_by_id(
            self,
            session: Session,
            account_id: int
    ) -> Optional[Account]:
        pass

    @abstractmethod
    def find_by_email_and_login_type(
            self, session: Session, email: str, login_type: LoginType
    ) -> Optional[Account]:
        pass
