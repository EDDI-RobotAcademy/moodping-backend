SYSTEM_PROMPT = (
    "당신은 따뜻한 심리 상담사입니다. "
    "주간 감정 데이터를 보고 2-3문단으로 짧게 요약하세요. "
    "각 문단 앞에 이모지 하나. "
    '반드시 다음 JSON만 응답: {"summary_text": "내용"} '
    "JSON 외 텍스트 없음."
)


def build(records: list[dict], avg_intensity: float, mood_counts: dict[str, int]) -> str:
    record_lines = []
    for r in records[:10]:
        record_lines.append(
            f"  - {r['record_date']} | {r['mood_emoji']} "
            f"(강도 {r['intensity']}/10) | {r.get('mood_text', '없음')[:30]}"
        )
    records_text = "\n".join(record_lines)

    mood_summary = ", ".join(
        f"{e}({c}회)"
        for e, c in sorted(mood_counts.items(), key=lambda x: -x[1])[:5]
    )

    return (
        f"[데이터] 기록 {len(records)}건, 평균강도 {avg_intensity:.1f}/10\n"
        f"감정분포: {mood_summary}\n\n"
        f"[기록]\n{records_text}\n\n"
        f"[작성] 2-3문단으로: 1)이번 주 요약 2)주목할 감정 3)한 가지 행동 제안. "
        f'JSON만: {{"summary_text": "내용"}}'
    )
