"""
더미 감정 기록 7일치 (하루 2건씩, 총 14건).
리얼한 감정 패턴: 긍정 4, 중립 3, 부정 7
"""
from datetime import date, datetime, timedelta


def get_dummy_week_range() -> tuple[date, date]:
    today = date.today()
    days_since_monday = today.weekday()
    this_monday = today - timedelta(days=days_since_monday)
    last_monday = this_monday - timedelta(days=7)
    last_sunday = this_monday - timedelta(days=1)
    return last_monday, last_sunday


def get_dummy_records() -> list[dict]:
    week_start, _ = get_dummy_week_range()

    records = [
        {"day_offset": 0, "mood_emoji": "happy",     "intensity": 7, "mood_text": "오랜만에 친구를 만나서 기분이 좋았다"},
        {"day_offset": 0, "mood_emoji": "calm",      "intensity": 5, "mood_text": "저녁에 산책하면서 마음이 편안해졌어"},
        {"day_offset": 1, "mood_emoji": "anxious",   "intensity": 8, "mood_text": "내일 발표가 있어서 너무 긴장돼"},
        {"day_offset": 1, "mood_emoji": "tired",     "intensity": 6, "mood_text": "준비하느라 밤을 새웠는데 피곤하다"},
        {"day_offset": 2, "mood_emoji": "excited",   "intensity": 9, "mood_text": "발표가 잘 끝나서 너무 신나!"},
        {"day_offset": 2, "mood_emoji": "annoyed",   "intensity": 4, "mood_text": "동료가 약속을 깜빡해서 좀 짜증났어"},
        {"day_offset": 3, "mood_emoji": "gloomy",    "intensity": 3, "mood_text": "비가 와서 그런지 기분이 가라앉았다"},
        {"day_offset": 3, "mood_emoji": "sad",       "intensity": 5, "mood_text": "옛날 사진을 보니까 슬퍼졌어"},
        {"day_offset": 4, "mood_emoji": "numb",      "intensity": 5, "mood_text": "특별한 일 없이 하루가 지나갔다"},
        {"day_offset": 4, "mood_emoji": "angry",     "intensity": 7, "mood_text": "뉴스 보다가 화가 많이 났어"},
        {"day_offset": 5, "mood_emoji": "love",      "intensity": 8, "mood_text": "가족이랑 맛있는 저녁을 먹었다"},
        {"day_offset": 5, "mood_emoji": "scared",    "intensity": 3, "mood_text": "건강검진 결과가 걱정돼"},
        {"day_offset": 6, "mood_emoji": "confident", "intensity": 8, "mood_text": "운동하고 나니까 자신감이 붙었다"},
        {"day_offset": 6, "mood_emoji": "calm",      "intensity": 6, "mood_text": "일요일이라 느긋하게 보냈어"},
    ]

    result = []
    for r in records:
        record_date = week_start + timedelta(days=r["day_offset"])
        result.append({
            "mood_emoji": r["mood_emoji"],
            "intensity": r["intensity"],
            "mood_text": r["mood_text"],
            "record_date": record_date,
            "recorded_at": datetime.combine(record_date, datetime.min.time().replace(hour=10 + r["day_offset"] % 12)),
        })

    return result


EMOJI_MAP = {
    "happy": "😊", "excited": "😄", "thrilled": "😍",
    "love": "🥰", "confident": "😎", "calm": "😌",
    "numb": "😐", "tired": "😴", "gloomy": "😔",
    "sad": "😢", "tearful": "😭", "annoyed": "😤",
    "angry": "😡", "anxious": "😰", "scared": "😨",
}

LABEL_KO = {
    "happy": "기쁨", "excited": "신남", "thrilled": "설렘",
    "love": "사랑", "confident": "자신감", "calm": "평온",
    "numb": "무감각", "tired": "피곤", "gloomy": "우울",
    "sad": "슬픔", "tearful": "눈물", "annoyed": "짜증",
    "angry": "분노", "anxious": "불안", "scared": "두려움",
}
