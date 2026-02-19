from abc import ABC, abstractmethod

from account.domain.entity.account import Account
from kakao_authentication.service.response.kakao_login_response import KakaoLoginResponse
from kakao_authentication.service.response.kakao_token_response import KakaoTokenResponse


class KakaoAuthenticationService(ABC):

    @abstractmethod
    def generate_oauth_url(self) -> str:
        pass

    @abstractmethod
    def request_access_token(self, code: str) -> KakaoTokenResponse:
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> Account:
        pass

    @abstractmethod
    def login_with_kakao(self, code: str) -> KakaoLoginResponse:
        pass
