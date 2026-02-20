from abc import abstractmethod, ABC
from typing import List

from board.domain.entity.board import Board


class BoardService(ABC):

    @abstractmethod
    def create_board(self, account_id: int, title: str, content: str) -> Board:
        pass

    @abstractmethod
    def list_boards(self, page: int = 1, page_size: int = 10) -> dict:
        pass

    @abstractmethod
    def read_board(self, board_id: int) -> Board:
        pass

    @abstractmethod
    def update_board(self, account_id: int, board_id: int, title: str | None, content: str | None) -> Board:
        pass

    @abstractmethod
    def delete_board(self, board_id: int, account_id: int):
        pass

    @abstractmethod
    def count_boards(self) -> int:
        pass
