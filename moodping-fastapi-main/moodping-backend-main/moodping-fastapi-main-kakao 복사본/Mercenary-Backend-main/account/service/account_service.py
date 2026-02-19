from abc import ABC, abstractmethod
from typing import Optional

from account.domain.entity.account import Account
from account.domain.value_objects.email import Email
from account.domain.value_objects.login_type import LoginType
from account.domain.value_objects.nickname import Nickname


class AccountService(ABC):

    @abstractmethod
    def register(
            self,
            login_type: str,
            email: Email,
            nickname: Nickname
    ) -> Account:
        pass

    @abstractmethod
    def find_by_email_and_login_type(
            self, email: Email, login_type: LoginType
    ) -> Optional[Account]:
        pass

    @abstractmethod
    def lookup(self, account_id: int) -> Account:
        pass
