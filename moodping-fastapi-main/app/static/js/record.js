// 레이블 → 이모지 매핑 (DB에는 레이블 저장, 화면엔 이모지 표시)
const EMOJI_MAP = {
    happy:     '😊', excited:  '😄', thrilled: '😍',
    love:      '🥰', confident:'😎', calm:     '😌',
    numb:      '😐', tired:    '😴', gloomy:   '😔',
    sad:       '😢', tearful:  '😭', annoyed:  '😤',
    angry:     '😡', anxious:  '😰', scared:   '😨',
};

// 레이블 → 한국어 이름
const LABEL_KO = {
    happy:'기쁨', excited:'신남', thrilled:'설렘', love:'사랑', confident:'자신감',
    calm:'평온', numb:'무감각', tired:'피곤', gloomy:'우울', sad:'슬픔',
    tearful:'눈물', annoyed:'짜증', angry:'분노', anxious:'불안', scared:'두려움',
};

document.addEventListener('DOMContentLoaded', async () => {
    await fetchAuthUser();
    logEvent('record_screen_view');

    let recordData = {
        moodLabel: null,   // DB에 저장되는 값 (영어 레이블)
        intensity: null,
        moodText: ''
    };

    const sectionEmoji     = document.getElementById('section-emoji');
    const sectionIntensity = document.getElementById('section-intensity');
    const sectionNote      = document.getElementById('section-note');
    const sectionResult    = document.getElementById('section-result');
    const submitBtn        = document.getElementById('submit-btn');

    // ── Step 1: 이모지 선택 ──────────────────────────────────────
    const emojiButtons = document.querySelectorAll('.emoji-btn');
    emojiButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            emojiButtons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            recordData.moodLabel = btn.dataset.label;

            logEvent('emoji_selected', {label: recordData.moodLabel});
            activateSection(sectionIntensity);
        });
    });

    // ── Step 2: 강도 선택 (슬라이더) ────────────────────────────
    const intensitySlider  = document.getElementById('intensity-slider');
    const sliderDisplay    = document.getElementById('slider-value-display');
    const intensityConfirm = document.getElementById('intensity-confirm-btn');

    function updateSliderBackground(val) {
        const pct = (val / 10) * 100;
        intensitySlider.style.background =
            `linear-gradient(to right, #007bff 0%, #007bff ${pct}%, #e0e0e0 ${pct}%, #e0e0e0 100%)`;
    }

    intensitySlider.addEventListener('input', () => {
        const val = parseInt(intensitySlider.value);
        sliderDisplay.textContent = val;
        updateSliderBackground(val);
    });

    updateSliderBackground(parseInt(intensitySlider.value));

    intensityConfirm.addEventListener('click', () => {
        recordData.intensity = parseInt(intensitySlider.value);
        logEvent('intensity_selected', {intensity: recordData.intensity});
        activateSection(sectionNote);
    });

    // ── Step 3: 메모 입력 & 저장 ─────────────────────────────────
    const noteInput = document.getElementById('note-input');
    noteInput.addEventListener('focus', () => {
        logEvent('text_input_start');
    });

    submitBtn.addEventListener('click', async () => {
        recordData.moodText = noteInput.value.trim();
        const anonId = getAnonId();

        sectionResult.classList.add('visible');
        document.getElementById('loading-spinner').style.display = 'flex';
        document.getElementById('result-content').style.display = 'none';
        setTimeout(() => sectionResult.scrollIntoView({behavior: 'smooth', block: 'end'}), 100);
        submitBtn.disabled = true;

        try {
            const res = await fetch('/mood-records', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',
                body: JSON.stringify({
                    mood_emoji: recordData.moodLabel,   // DB에 영어 레이블 저장
                    intensity:  recordData.intensity,
                    mood_text:  recordData.moodText,
                    anon_id:    anonId
                })
            });

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }

            const result = await res.json();

            logEvent('record_complete', {record_id: result.record_id});

            document.getElementById('loading-spinner').style.display = 'none';
            document.getElementById('result-content').style.display = 'block';

            logEvent('analysis_view', {record_id: result.record_id, status: result.analysis_status});

            if (result.analysis_status === 'success' && result.analysis) {
                let text = result.analysis.analysis_text || '';

                // 백엔드 파싱 실패로 raw JSON이 그대로 내려온 경우 한 번 더 파싱
                if (text.trim().startsWith('{')) {
                    try {
                        const inner = JSON.parse(text);
                        if (inner.analysis_text) text = inner.analysis_text;
                    } catch (_) {}
                }

                const formatted = text.replace(/\n/g, '<br>');
                document.getElementById('feedback-text').innerHTML = formatted;
            } else {
                document.getElementById('feedback-text').textContent =
                    '기록은 정상적으로 저장되었으나 AI 분석을 불러오지 못했습니다.';
            }

        } catch (error) {
            console.error('오류:', error);
            alert('서버 통신 중 오류가 발생했습니다.');
            submitBtn.disabled = false;
            sectionResult.classList.remove('visible');
        }
    });

    // ── 최종 확인 버튼 ────────────────────────────────────────────
    document.getElementById('confirm-btn').addEventListener('click', () => {
        logEvent('feedback_confirmed');
        window.location.href = '/';
    });

    // ── 섹션 활성화 헬퍼 ─────────────────────────────────────────
    function activateSection(element) {
        if (element.classList.contains('disabled-section')) {
            element.classList.remove('disabled-section');
            element.classList.add('active-section');
            setTimeout(() => element.scrollIntoView({behavior: 'smooth', block: 'center'}), 100);
        }
    }
});
