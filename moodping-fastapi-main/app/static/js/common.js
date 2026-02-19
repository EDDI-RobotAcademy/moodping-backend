// UUID Generation (Public Domain/MIT)
function generateUUID() {
    var d = new Date().getTime();
    var d2 = ((typeof performance !== 'undefined') && performance.now && (performance.now() * 1000)) || 0;
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16;
        if (d > 0) {
            r = (d + r) % 16 | 0;
            d = Math.floor(d / 16);
        } else {
            r = (d2 + r) % 16 | 0;
            d2 = Math.floor(d2 / 16);
        }
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

// 비로그인 사용자 익명 ID (localStorage에 영속 저장)
function getAnonId() {
    let anonId = localStorage.getItem('anon_id');
    if (!anonId) {
        anonId = generateUUID();
        localStorage.setItem('anon_id', anonId);
    }
    return anonId;
}

// 로그인 상태
let authUser = { logged_in: false, user_id: null, nickname: null };

async function fetchAuthUser() {
    try {
        const res = await fetch('/auth/me', { credentials: 'include' });
        const d = await res.json();
        authUser = { logged_in: !!d.logged_in, user_id: d.user_id || null, nickname: d.nickname || null };
    } catch (e) {
        authUser = { logged_in: false, user_id: null, nickname: null };
    }
    return authUser;
}

// 세션 ID (sessionStorage: 탭 닫으면 초기화)
function getSessionId() {
    let sessionId = sessionStorage.getItem('session_id');
    if (!sessionId) {
        sessionId = generateUUID();
        sessionStorage.setItem('session_id', sessionId);
    }
    return sessionId;
}

/**
 * 이벤트 로그 전송 (POST /api/events)
 * event_id는 매 호출마다 새로운 UUID 생성 → 중복 저장 방지
 */
async function logEvent(eventName, extraData = {}) {
    const anonId = getAnonId();
    const sessionId = getSessionId();

    try {
        await fetch('/api/events', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({
                event_id: generateUUID(),
                session_id: sessionId,
                user_id: authUser.logged_in ? authUser.user_id : null,
                anon_id: anonId,
                event_name: eventName,
                extra_data: extraData
            })
        });
    } catch (error) {
        console.error('이벤트 로깅 실패:', error);
    }
}
