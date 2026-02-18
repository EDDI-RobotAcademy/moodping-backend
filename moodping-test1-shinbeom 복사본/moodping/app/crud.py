from sqlalchemy.orm import Session
from . import models, schemas
import uuid

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Check if user exists first to be safe, though ID should be unique
    existing_user = get_user(db, user.user_id)
    if existing_user:
        return existing_user
    db_user = models.User(user_id=user.user_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_emotion_record(db: Session, record: schemas.EmotionRecordCreate):
    db_record = models.EmotionRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def create_event_log(db: Session, event: schemas.EventLogCreate):
    db_event = models.EventLog(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def create_feedback(db: Session, record_id: int, content: str):
    db_feedback = models.AIFeedback(record_id=record_id, content=content)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback
