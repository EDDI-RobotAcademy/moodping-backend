"""
LLM 프롬프트 빌더.

intensity 범위에 따라 3가지 톤으로 분기:
  - 7~10 : 긍정/칭찬 (업무 성과 연결, MP-B-22 검증 조건 반영)
  - 0~4  : 공감 위주 (CBT 재프레이밍, moodping 원본 feedback.py 구조 참고)
  - 5~6  : 중립 (균형 있는 메타인지 안내)
"""

from app.domain.mood.models import MoodRecord

SYSTEM_PROMPT = (
    "당신은 인지행동치료(CBT)와 메타인지(Metacognition) 이론에 정통한 심리 전문가입니다. "
    "사용자의 감정 데이터(이모지·강도·메모)를 구체적으로 반영하여 따뜻하고 실용적인 조언을 제공합니다. "
    "각 문단 앞에 어울리는 이모지 하나를 붙이고, 총 3문단으로 작성합니다. "
    "1문단: 사용자가 입력한 내용을 직접 언급하며 감정을 공감. "
    "2문단: CBT 관점으로 감정을 재해석하거나 실질적 행동 제안. "
    "3문단: 오늘 당장 실천할 수 있는 구체적인 한 가지 행동 제안으로 마무리. "
    "반드시 다음 JSON 형식으로만 응답하세요: {\"analysis_text\": \"내용\"} "
    "JSON 외 다른 텍스트, 코드 블록, 마크다운 기호를 절대 포함하지 마세요."
)


EMOJI_MAP: dict[str, str] = {
    "happy": "😊", "excited": "😄", "thrilled": "😍",
    "love": "🥰", "confident": "😎", "calm": "😌",
    "numb": "😐", "tired": "😴", "gloomy": "😔",
    "sad": "😢", "tearful": "😭", "annoyed": "😤",
    "angry": "😡", "anxious": "😰", "scared": "😨",
}

LABEL_KO: dict[str, str] = {
    "happy": "기쁨", "excited": "신남", "thrilled": "설렘",
    "love": "사랑", "confident": "자신감", "calm": "평온",
    "numb": "무감각", "tired": "피곤", "gloomy": "우울",
    "sad": "슬픔", "tearful": "눈물", "annoyed": "짜증",
    "angry": "분노", "anxious": "불안", "scared": "두려움",
}


def build(record: MoodRecord) -> str:
    """MoodRecord를 받아 intensity 기반 프롬프트 문자열을 반환합니다."""
    note = record.mood_text if record.mood_text and record.mood_text.strip() else "별도의 메모 없음"

    if record.intensity >= 7:
        return _positive(record, note)
    elif record.intensity <= 4:
        return _empathy(record, note)
    else:
        return _neutral(record, note)


def _emotion_context(record: MoodRecord) -> str:
    """mood_emoji(레이블)에서 이모지와 한국어 이름을 반환합니다."""
    label = record.mood_emoji  # DB에 저장된 영어 레이블
    emoji = EMOJI_MAP.get(label, "")
    ko    = LABEL_KO.get(label, label)
    return f"{emoji} {ko}({label})"


def _positive(record: MoodRecord, note: str) -> str:
    emotion = _emotion_context(record)
    return (
        f"[사용자 감정 데이터]\n"
        f"- 감정: {emotion}\n"
        f"- 감정 강도: {record.intensity}점 / 10점\n"
        f"- 감정 메모: {note}\n\n"
        f"[작성 지침]\n"
        f"1문단: '{emotion}' 감정과 {record.intensity}점이라는 높은 강도를 직접 언급하며, "
        f"메모 내용({note})이 구체적으로 반영된 공감 표현으로 시작하세요.\n"
        f"2문단: 이 긍정 에너지가 오늘 어떤 구체적인 상황에 도움이 될 수 있는지 실질적으로 제안하세요. "
        f"막연한 칭찬이 아닌, 행동과 연결된 구체적 예시를 포함하세요.\n"
        f"3문단: 오늘 이 에너지를 유지하기 위해 당장 실천할 수 있는 한 가지 작은 행동을 제안하며 마무리하세요.\n"
        f"각 문단 앞에 어울리는 이모지를 하나씩 붙이세요. "
        f'반드시 {{"analysis_text": "내용"}} JSON 형식으로만 응답하세요. 코드 블록 금지.'
    )


def _empathy(record: MoodRecord, note: str) -> str:
    emotion = _emotion_context(record)
    return (
        f"[사용자 감정 데이터]\n"
        f"- 감정: {emotion}\n"
        f"- 감정 강도: {record.intensity}점 / 10점\n"
        f"- 감정 메모: {note}\n\n"
        f"[작성 지침]\n"
        f"1문단: '{emotion}' 감정과 강도 {record.intensity}점, "
        f"그리고 메모({note})를 직접 인용하며 이 감정이 완전히 자연스럽고 타당하다는 것을 충분히 공감하세요.\n"
        f"2문단: CBT 재프레이밍 — 이 감정이 개인적 결함이 아닌 특정 상황에서 생긴 반응임을 구체적으로 설명하고, "
        f"자기 비판 대신 어떤 시각으로 볼 수 있는지 실용적으로 제안하세요.\n"
        f"3문단: 지금 당장 할 수 있는 작은 행동(예: 5분 산책, 따뜻한 음료, 깊게 숨 쉬기 등) 한 가지를 "
        f"친근하고 따뜻하게 제안하며 마무리하세요.\n"
        f"각 문단 앞에 어울리는 이모지를 하나씩 붙이세요. "
        f'반드시 {{"analysis_text": "내용"}} JSON 형식으로만 응답하세요. 코드 블록 금지.'
    )


def _neutral(record: MoodRecord, note: str) -> str:
    emotion = _emotion_context(record)
    return (
        f"[사용자 감정 데이터]\n"
        f"- 감정: {emotion}\n"
        f"- 감정 강도: {record.intensity}점 / 10점\n"
        f"- 감정 메모: {note}\n\n"
        f"[작성 지침]\n"
        f"1문단: '{emotion}' 감정과 강도 {record.intensity}점을 직접 언급하며, "
        f"메모({note})에 담긴 감정을 인식하고 기록했다는 것 자체를 따뜻하게 인정하세요.\n"
        f"2문단: 중립적 상태가 오히려 자신을 돌아볼 좋은 기회임을 설명하고, "
        f"이 상태에서 에너지를 소비하지 않고 회복할 수 있는 구체적 방법을 제안하세요.\n"
        f"3문단: 오늘 딱 하나, 가장 쉽게 실천할 수 있는 자기 돌봄 행동을 제안하며 마무리하세요.\n"
        f"각 문단 앞에 어울리는 이모지를 하나씩 붙이세요. "
        f'반드시 {{"analysis_text": "내용"}} JSON 형식으로만 응답하세요. 코드 블록 금지.'
    )
