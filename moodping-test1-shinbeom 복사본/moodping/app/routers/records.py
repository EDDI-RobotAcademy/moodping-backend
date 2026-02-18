from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(
    prefix="/api/records",
    tags=["records"],
)

@router.post("/", response_model=schemas.EmotionRecord)
def create_record(record: schemas.EmotionRecordCreate, db: Session = Depends(database.get_db)):
    # Ensure user exists
    user = crud.get_user(db, record.user_id)
    if not user:
        crud.create_user(db, schemas.UserCreate(user_id=record.user_id))
    return crud.create_emotion_record(db, record=record)
