/* ParkEase API client - uses httpOnly cookies for authentication */
const API = (() => {
  const BASE = '/api';
  const userStore = {
    get user() {
      try { return JSON.parse(localStorage.getItem('parkease_user')); }
      catch (e) { return null; }
    },
    set user(u) { u ? localStorage.setItem('parkease_user', JSON.stringify(u)) : localStorage.removeItem('parkease_user'); },
    clear() { this.user = null; }
  };

  function getCsrfToken() {
    const match = document.cookie.match(/(?:^|; )csrf_access_token=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
  }

  let refreshPromise = null;

  function refreshToken() {
    if (refreshPromise) return refreshPromise;
    const csrf = getCsrfToken();
    const headers = { 'Content-Type': 'application/json' };
    if (csrf) headers['X-CSRF-TOKEN'] = csrf;
    refreshPromise = fetch(`${BASE}/auth/refresh`, { method: 'POST', credentials: 'include', headers })
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          return data.access_token;
        }
        throw new Error('Refresh failed');
      })
      .finally(() => { refreshPromise = null; });
    return refreshPromise;
  }

  async function request(path, { method = 'GET', body = null } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    const csrf = getCsrfToken();
    if (csrf && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
      headers['X-CSRF-TOKEN'] = csrf;
    }

    const opts = { method, headers, credentials: 'include' };
    if (body) opts.body = JSON.stringify(body);

    let res = await fetch(BASE + path, opts);

    // Try a token refresh once on 401
    if (res.status === 401) {
      try {
        await refreshToken();
        res = await fetch(BASE + path, opts);
      } catch (e) {
        userStore.clear();
        Auth.flagSessionExpired();
      }
    }

    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const data = await res.json();
      return { ok: res.ok, status: res.status, data };
    }
    const text = await res.text();
    return { ok: res.ok, status: res.status, data: text };
  }

  function handleError(err) {
    let message = 'Something went wrong. Please try again.';
    if (err && typeof err === 'object') {
      const d = err.data;
      if (typeof d === 'string' && d) message = d;
      else if (d && d.error) message = d.error;
      else if (d && d.message) message = d.message;
      else if (d && d.msg) message = d.msg;
    }
    return { ok: false, status: err && err.status, message };
  }

  function ensureOk(res) {
    if (!res.ok) throw Object.assign(new Error('Request failed'), { ok: res.ok, status: res.status, data: res.data });
    return res.data;
  }

  // Payment screenshots sit behind auth, but an <img src> cannot carry the
  // Bearer header - it would depend entirely on the access-token cookie being
  // present. Fetch with the header and hand back an object URL instead, so the
  // image renders even when the cookie is missing or blocked.
  async function fetchImage(path) {
    const url = path.startsWith('/') ? path : '/' + path;
    let res = await fetch(url, { credentials: 'include' });
    if (res.status === 401) {
      await refreshToken();
      res = await fetch(url, { credentials: 'include' });
    }
    if (!res.ok) throw Object.assign(new Error('Image request failed'), { status: res.status });
    return URL.createObjectURL(await res.blob());
  }

  return {
    get: (p) => request(p),
    post: (p, body) => request(p, { method: 'POST', body }),
    put: (p, body) => request(p, { method: 'PUT', body }),
    del: (p) => request(p, { method: 'DELETE' }),
    request,
    ensureOk,
    handleError,
    fetchImage,
    getCsrfToken,
    userStore
  };
})();

const Auth = (() => {
  function onAuthChange() {
    const user = API.userStore.user;
    if (typeof window.AuthChanged === 'function') window.AuthChanged(user);
  }
  function saveSession(data) {
    if (data.user) API.userStore.user = data.user;
    onAuthChange();
  }
  function logout() {
    API.userStore.clear();
    const csrf = API.getCsrfToken();
    const headers = { 'Content-Type': 'application/json' };
    if (csrf) headers['X-CSRF-TOKEN'] = csrf;
    fetch('/api/auth/logout', { method: 'POST', credentials: 'include', headers }).catch(() => {});
    onAuthChange();
  }
  function flagSessionExpired() {
    if (window.Parkease) Parkease.showToast('Your session has expired. Please sign in again.', 'warning');
  }
  return {
    isLoggedIn() { return !!API.userStore.user; },
    get user() { return API.userStore.user; },
    saveSession,
    logout,
    flagSessionExpired
  };
})();

window.Auth = Auth;
window.API = API;