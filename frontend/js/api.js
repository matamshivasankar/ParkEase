/* ParkEase API client */
const API = (() => {
  const BASE = '/api';
  const TOKEN_KEY = 'parkease_access_token';
  const userStore = {
    get token() { return localStorage.getItem(TOKEN_KEY); },
    set token(v) { v ? localStorage.setItem(TOKEN_KEY, v) : localStorage.removeItem(TOKEN_KEY); },
    get user() {
      try { return JSON.parse(localStorage.getItem('parkease_user')); }
      catch (e) { return null; }
    },
    set user(u) { u ? localStorage.setItem('parkease_user', JSON.stringify(u)) : localStorage.removeItem('parkease_user'); },
    clear() { this.token = null; this.user = null; }
  };

  let refreshPromise = null;

  function refreshToken() {
    if (refreshPromise) return refreshPromise;
    refreshPromise = fetch(`${BASE}/auth/refresh`, { method: 'POST', credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          userStore.token = data.access_token;
          return data.access_token;
        }
        throw new Error('Refresh failed');
      })
      .finally(() => { refreshPromise = null; });
    return refreshPromise;
  }

  async function request(path, { method = 'GET', body = null } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (userStore.token) headers.Authorization = `Bearer ${userStore.token}`;

    const opts = { method, headers, credentials: 'include' };
    if (body) opts.body = JSON.stringify(body);

    let res = await fetch(BASE + path, opts);

    // Try a token refresh once on 401
    if (res.status === 401 && userStore.token) {
      try {
        const newToken = await refreshToken();
        headers.Authorization = `Bearer ${newToken}`;
        opts.headers = headers;
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

  return {
    get: (p) => request(p),
    post: (p, body) => request(p, { method: 'POST', body }),
    put: (p, body) => request(p, { method: 'PUT', body }),
    del: (p) => request(p, { method: 'DELETE' }),
    request,
    ensureOk,
    handleError,
    userStore
  };
})();

const Auth = (() => {
  function onAuthChange() {
    const user = API.userStore.user;
    if (typeof window.AuthChanged === 'function') window.AuthChanged(user);
  }
  function saveSession(data) {
    if (data.access_token) API.userStore.token = data.access_token;
    if (data.user) API.userStore.user = data.user;
    onAuthChange();
  }
  function logout() {
    API.userStore.clear();
    fetch('/api/auth/logout', { method: 'POST', credentials: 'include' }).catch(() => {});
    onAuthChange();
  }
  function flagSessionExpired() {
    if (window.Parkease) Parkease.showToast('Your session has expired. Please sign in again.', 'warning');
  }
  return {
    isLoggedIn() { return !!(API.userStore.token || API.userStore.user); },
    get user() { return API.userStore.user; },
    saveSession,
    logout,
    flagSessionExpired
  };
})();