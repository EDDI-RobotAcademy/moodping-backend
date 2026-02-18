from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    emotion_records = relationship("EmotionRecord", back_populates="user")
    event_logs = relationship("EventLog", back_populates="user")

class EmotionRecord(Base):
    __tablename__ = "emotion_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"))
    emotion_type = Column(String(50))  # e.g., "JOY", "SADNESS", etc.
    intensity = Column(Integer)  # 1-5
    note = Column(String(300), nullable=True) # Increased limit to 300 chars
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="emotion_records")
    ai_feedback = relationship("AIFeedback", back_populates="record", uselist=False)

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    event_type = Column(String(50)) # record_start, emoji_selected, etc.
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(Text, nullable=True) # JSON string for flexibility

    user = relationship("User", back_populates="event_logs")

class AIFeedback(Base):
    __tablename__ = "ai_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("emotion_records.id"))
    content = Column(Text)
    is_helpful = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    record = relationship("EmotionRecord", back_populates="ai_feedback")
