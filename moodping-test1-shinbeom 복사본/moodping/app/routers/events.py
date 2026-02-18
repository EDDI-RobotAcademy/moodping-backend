from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
)

@router.post("/", response_model=schemas.EventLog)
def create_event(event: schemas.EventLogCreate, db: Session = Depends(database.get_db)):
    if event.user_id:
        user = crud.get_user(db, event.user_id)
        if not user:
             crud.create_user(db, schemas.UserCreate(user_id=event.user_id))
    return crud.create_event_log(db, event=event)

@router.get("/funnel")
def get_funnel_stats(db: Session = Depends(database.get_db)):
    # Simple placeholder for funnel stats
    # Ideally this would do complex aggregation
    return {"message": "Funnel stats not implemented yet"}
