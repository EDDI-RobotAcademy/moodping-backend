from fastapi import Cookie, Query
from authentication.service.authentication_service_impl import AuthenticationServiceImpl

from fastapi import APIRouter, Depends, HTTPException

from board.controller.request.create_board_request import CreateBoardRequest
from board.controller.request.update_board_request import UpdateBoardRequest
from board.service.board_service_impl import BoardServiceImpl


board_router = APIRouter(prefix="/board")

def inject_board_service() -> BoardServiceImpl:
    return BoardServiceImpl.get_instance()

def inject_auth_service() -> AuthenticationServiceImpl:
    return AuthenticationServiceImpl.get_instance()


def get_authenticated_account_id(
    userToken: str = Cookie(None),
    auth_service: AuthenticationServiceImpl = Depends(inject_auth_service),
) -> int:

    if not userToken:
        raise HTTPException(status_code=401, detail="Authentication required")

    print(f"userToken: {userToken}")

    account_id = auth_service.validate_session(userToken)
    print(f"account_id: {account_id}")

    if not account_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return account_id

@board_router.post("/create")
def create_board(
    request: CreateBoardRequest,
    account_id: int = Depends(get_authenticated_account_id),
    board_service: BoardServiceImpl = Depends(inject_board_service),
):
    try:
        board = board_service.create_board(
            account_id=account_id,
            title=request.title,
            content=request.content,
        )

        return {
            "id": board.id,
            "title": board.title,
            "content": board.content,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@board_router.get("/list")
def list_boards(
    page: int = Query(1, ge=1, description="페이지 번호, 1 이상"),
    page_size: int = Query(10, ge=1, le=100, description="한 페이지 아이템 수"),
    board_service: BoardServiceImpl = Depends(inject_board_service),
):
    try:
        boards = board_service.list_boards(page=page, page_size=page_size)

        return {
            "page": page,
            "page_size": page_size,
            **boards
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@board_router.get("/read/{board_id}")
def get_board(
    board_id: int,
    board_service: BoardServiceImpl = Depends(inject_board_service),
):
    try:
        board = board_service.read_board(board_id)
        return {
            "id": board.id,
            "title": board.title,
            "content": board.content,
            "account_id": board.account_id,
            "created_at": board.created_at,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@board_router.put("/update/{board_id}")
def update_board(
    board_id: int,
    request: UpdateBoardRequest,
    account_id: int = Depends(get_authenticated_account_id),
    board_service: BoardServiceImpl = Depends(inject_board_service),
):
    try:
        board = board_service.update_board(
            account_id=account_id,
            board_id=board_id,
            title=request.title,
            content=request.content
        )
        return {
            "id": board.id,
            "title": board.title,
            "content": board.content,
            "account_id": board.account_id,
            "created_at": board.created_at,
            "updated_at": board.updated_at
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@board_router.delete("/delete/{board_id}")
def delete_board(
    board_id: int,
    account_id: int = Depends(get_authenticated_account_id),
    board_service: BoardServiceImpl = Depends(inject_board_service)
):
    try:
        board_service.delete_board(board_id=board_id, account_id=account_id)
        return {"board_id": board_id, "status": "deleted"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
