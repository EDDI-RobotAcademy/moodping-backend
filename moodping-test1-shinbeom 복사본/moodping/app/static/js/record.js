document.addEventListener('DOMContentLoaded', () => {
    logEvent('record_screen_view');

    let recordData = {
        emotion_type: null,
        intensity: null,
        note: ""
    };

    // --- Sections ---
    const sectionEmoji = document.getElementById('section-emoji');
    const sectionIntensity = document.getElementById('section-intensity');
    const sectionNote = document.getElementById('section-note');
    const sectionResult = document.getElementById('section-result');
    const submitBtn = document.getElementById('submit-btn');

    // --- Step 1: Emoji Selection ---
    const emojis = document.querySelectorAll('.emoji-btn');
    emojis.forEach(btn => {
        btn.addEventListener('click', () => {
            // UI Update
            emojis.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            
            // Data Update
            recordData.emotion_type = btn.dataset.value;
            
            // Log & Activate Next
            logEvent('emoji_selected', { emotion: recordData.emotion_type });
            activateSection(sectionIntensity);
        });
    });

    // --- Step 2: Intensity Selection ---
    const intensities = document.querySelectorAll('.intensity-btn');
    intensities.forEach(btn => {
        btn.addEventListener('click', () => {
            // UI Update
            intensities.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            
            // Data Update
            recordData.intensity = parseInt(btn.dataset.value);
            
            // Log & Activate Next
            logEvent('intensity_selected', { intensity: recordData.intensity });
            activateSection(sectionNote);
        });
    });

    // --- Step 3: Note & Submit ---
    const noteInput = document.getElementById('note-input');
    noteInput.addEventListener('focus', () => {
        logEvent('text_input_start');
    });

    submitBtn.addEventListener('click', async () => {
        recordData.note = noteInput.value;
        const userId = getUserId();
        
        // Show Loading UI (Result section is hidden, not disabled, so we use classList logic differently or just display block)
        sectionResult.classList.add('visible'); // Show result container
        document.getElementById('loading-spinner').style.display = 'flex';
        document.getElementById('result-content').style.display = 'none';
        
        // Scroll to result
        setTimeout(() => {
             sectionResult.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 100);

        submitBtn.disabled = true; // Disable submit to prevent double click

        try {
            // 1. Save Record
            const response = await fetch('/api/records/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    emotion_type: recordData.emotion_type,
                    intensity: recordData.intensity,
                    note: recordData.note
                })
            });

            if (response.ok) {
                const result = await response.json();
                logEvent('record_complete', { record_id: result.id });
                
                // 2. Get AI Feedback
                const feedbackRes = await fetch(`/api/feedback/?record_id=${result.id}`, {
                    method: 'POST'
                });
                const feedbackData = await feedbackRes.json();
                
                // Show Result
                document.getElementById('loading-spinner').style.display = 'none';
                document.getElementById('result-content').style.display = 'block';
                
                // Simple Markdown Parser: **Bold** -> <strong>, Newlines -> <br>
                const formattedContent = feedbackData.content
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n/g, '<br>');
                
                document.getElementById('feedback-text').innerHTML = formattedContent;
                
            } else {
                alert('기록 저장에 실패했습니다. 다시 시도해주세요.');
                submitBtn.disabled = false;
                sectionResult.classList.remove('visible');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('서버 통신 중 오류가 발생했습니다.');
            submitBtn.disabled = false;
            sectionResult.classList.remove('visible');
        }
    });

    // --- Final Step: Confirm ---
    document.getElementById('confirm-btn').addEventListener('click', () => {
        logEvent('feedback_confirmed').then(() => {
            window.location.href = '/';
        });
    });

    // --- Helper: Activate Section ---
    function activateSection(element) {
        if (element.classList.contains('disabled-section')) {
            element.classList.remove('disabled-section');
            element.classList.add('active-section');
            
            // Smooth scroll to the newly activated section
            setTimeout(() => {
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
    }
});
