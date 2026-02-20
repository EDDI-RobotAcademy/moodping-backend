from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from board.domain.entity.board import Board


class BoardRepository(ABC):

    @abstractmethod
    def save(self, session: Session, board: Board) -> Board:
        pass

    @abstractmethod
    def find_all(self, session: Session, offset: int = 0, limit: int = 10) -> list[Board]:
        pass

    @abstractmethod
    def find_by_id(self, session: Session, board_id: int) -> Board | None:
        pass

    @abstractmethod
    def delete(self, session: Session, board: Board):
        pass

    @abstractmethod
    def count_all(self, session: Session) -> int:
        pass
