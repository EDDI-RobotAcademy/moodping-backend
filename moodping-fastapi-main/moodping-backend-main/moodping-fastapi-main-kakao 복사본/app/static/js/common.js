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

function getAnonId() {
    let anonId = localStorage.getItem('anon_id');
    if (!anonId) {
        anonId = generateUUID();
        localStorage.setItem('anon_id', anonId);
    }
    return anonId;
}

function getSessionId() {
    let sessionId = sessionStorage.getItem('session_id');
    if (!sessionId) {
        sessionId = generateUUID();
        sessionStorage.setItem('session_id', sessionId);
    }
    return sessionId;
}

function getToken() {
    return localStorage.getItem('mp_token');
}

function setToken(token) {
    localStorage.setItem('mp_token', token);
}

function removeToken() {
    localStorage.removeItem('mp_token');
}

function isLoggedIn() {
    return !!getToken();
}

function getAuthHeaders() {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

async function fetchUserInfo() {
    const token = getToken();
    if (!token) return null;
    try {
        const res = await fetch('/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            removeToken();
            return null;
        }
        return await res.json();
    } catch {
        return null;
    }
}

function handleTokenFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token) {
        setToken(token);
        window.history.replaceState({}, '', window.location.pathname);
    }
}

async function logEvent(eventName, extraData = {}) {
    const anonId = getAnonId();
    const sessionId = getSessionId();

    try {
        await fetch('/api/events', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                event_id: generateUUID(),
                session_id: sessionId,
                user_id: null,
                anon_id: anonId,
                event_name: eventName,
                extra_data: extraData
            })
        });
    } catch (error) {
        console.error('이벤트 로깅 실패:', error);
    }
}

function renderNavAuth(navActionsEl) {
    if (!navActionsEl) return;

    if (isLoggedIn()) {
        fetchUserInfo().then(user => {
            if (!user) {
                navActionsEl.innerHTML = `<a href="/auth/kakao" class="btn-kakao">${kakaoIcon()} 로그인</a>`;
                return;
            }
            const img = user.profile_image
                ? `<img src="${user.profile_image}" alt="">`
                : '';
            navActionsEl.innerHTML = `
                <div class="nav-profile">
                    ${img}
                    <span>${user.nickname || '사용자'}</span>
                </div>
                <button class="btn-logout" onclick="logout()">로그아웃</button>
            `;
        });
    } else {
        navActionsEl.innerHTML = `<a href="/auth/kakao" class="btn-kakao">${kakaoIcon()} 로그인</a>`;
    }
}

function logout() {
    removeToken();
    window.location.href = '/';
}

function kakaoIcon() {
    return `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3C6.48 3 2 6.58 2 10.94c0 2.8 1.86 5.27 4.66 6.67-.15.56-.96 3.6-.99 3.83 0 0-.02.17.09.23.11.07.24.01.24.01.32-.04 3.7-2.44 4.28-2.86.56.08 1.14.12 1.72.12 5.52 0 10-3.58 10-7.94S17.52 3 12 3z"/></svg>`;
}
