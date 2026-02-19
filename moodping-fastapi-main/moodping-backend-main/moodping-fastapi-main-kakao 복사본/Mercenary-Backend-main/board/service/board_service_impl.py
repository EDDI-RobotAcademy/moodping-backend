from typing import List, Any

from sqlalchemy.orm import Session

from account.domain.entity.account import Account
from board.domain.entity.board import Board
from board.repository.board_repository_impl import BoardRepositoryImpl
from account.repository.account_repository_impl import AccountRepositoryImpl
from board.service.board_service import BoardService
from config.mysql_config import MySQLConfig


class BoardServiceImpl(BoardService):

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

    def __init__(self):
        self.board_repository = BoardRepositoryImpl.get_instance()
        self.account_repository = AccountRepositoryImpl.get_instance()

    def create_board(self, account_id: int, title: str, content: str) -> Board:

        session: Session = MySQLConfig().get_session()

        try:
            account = session.get(Account, account_id)

            if not account:
                raise ValueError("Account not found")

            board = Board.create(account_id, title, content)

            self.board_repository.save(session, board)

            session.commit()

            return board

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def list_boards(self, page: int = 1, page_size: int = 10) -> dict:
        offset = (page - 1) * page_size
        session = MySQLConfig().get_session()

        try:
            boards = self.board_repository.find_all(session, offset=offset, limit=page_size)
            result = [
                {
                    "id": b.id,
                    "title": b.title,
                    "content": b.content,
                    "author_nickname": b.account.profile.nickname,  # 세션 살아 있는 동안 접근
                    "created_at": b.created_at,
                }
                for b in boards
            ]
            total = self.board_repository.count_all(session)
            return {"boards": result, "total": total}

        finally:
            session.close()

    def read_board(self, board_id: int) -> Board:
        session: Session = MySQLConfig().get_session()
        try:
            board = self.board_repository.find_by_id(session, board_id)
            if not board:
                raise ValueError("Board not found")

            return board

        finally:
            session.close()

    def update_board(self, account_id: int, board_id: int, title: str | None, content: str | None) -> Board:
        session: Session = MySQLConfig().get_session()
        try:
            board = self.board_repository.find_by_id(session, board_id)
            if not board:
                raise ValueError("Board not found")

            if board.account_id != account_id:
                raise PermissionError("Not authorized to modify this board")

            if title is not None:
                board.title = title
            if content is not None:
                board.content = content

            session.commit()
            # refresh로 최신 상태 가져오기
            session.refresh(board)
            return board

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def delete_board(self, board_id: int, account_id: int):
        session: Session = MySQLConfig().get_session()
        try:
            board = self.board_repository.find_by_id(session, board_id)
            if not board:
                raise ValueError(f"Board with ID {board_id} not found")

            if board.account_id != account_id:
                raise PermissionError("You are not allowed to delete this board")

            self.board_repository.delete(session, board)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

    def count_boards(self) -> int:
        session = MySQLConfig().get_session()
        try:
            return self.board_repository.count_all(session)
        finally:
            session.close()
