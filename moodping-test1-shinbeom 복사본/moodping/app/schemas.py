from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    user_id: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EmotionRecordBase(BaseModel):
    user_id: str
    emotion_type: str
    intensity: int
    note: Optional[str] = None

class EmotionRecordCreate(EmotionRecordBase):
    pass

class EmotionRecord(EmotionRecordBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EventLogBase(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    event_type: str
    metadata_json: Optional[str] = None

class EventLogCreate(EventLogBase):
    pass

class EventLog(EventLogBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class FeedbackBase(BaseModel):
    content: str

class Feedback(FeedbackBase):
    id: int
    record_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
