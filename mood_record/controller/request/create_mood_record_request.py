from pydantic import BaseModel, Field, field_validator

class CreateMoodRecordRequest(BaseModel):
    mood_emoji: str = Field(..., min_length=1, description="감정 이모지 (예: 😊)")
    intensity: int = Field(..., ge=0, le=10, description="감정 강도 0~10")
    mood_text: str | None = Field(None, max_length=500, description="감정 설명 (선택, 500자 이내)")
    anon_id: str | None = Field(None, description="비로그인 사용자 익명 ID")

    @field_validator("mood_emoji")
    @classmethod
    def emoji_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("mood_emoji must not be empty")
        return v.strip()

    @field_validator("mood_text")
    @classmethod
    def mood_text_max_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("mood_text must not exceed 500 characters")
        return v
