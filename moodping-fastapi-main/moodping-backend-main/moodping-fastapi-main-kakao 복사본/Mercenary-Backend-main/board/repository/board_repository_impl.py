from sqlalchemy.orm import Session
from board.domain.entity.board import Board
from board.repository.board_repository import BoardRepository


class BoardRepositoryImpl(BoardRepository):

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

    def save(self, session: Session, board: Board) -> Board:
        session.add(board)
        return board

    def find_all(self, session: Session, offset: int = 0, limit: int = 10) -> list[Board]:
        return (
            session.query(Board)
            .order_by(Board.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def find_by_id(self, session: Session, board_id: int) -> Board | None:
        return session.get(Board, board_id)

    def delete(self, session: Session, board: Board):
        session.delete(board)

    def count_all(self, session: Session) -> int:
        return session.query(Board).count()
