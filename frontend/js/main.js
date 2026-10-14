/* ============ ParkEase Application ============ */
(function () {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ---------- Icons (Lucide-style stroke SVGs) ---------- */
  const I = {
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    star: '<svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    car: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11"/><path d="M4 11h16a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-1"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>',
    bike: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2zM22 17l-3.37-6.11a2 2 0 0 0-1.74-1.01H9"/></svg>',
    truck: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13" rx="1"/><path d="M16 8h4l3 3v5h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
    ev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"/></svg>',
    wallet: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/></svg>',
    activity: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    tag: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
    upload: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    eye: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    bell: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
    inbox: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>',
    refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>',
    shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    image: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
    cloudUpload: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 13v8"/><path d="M4 14.9A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.24"/><path d="m8 17 4-4 4 4"/></svg>',
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
  };
  const VEH_ICON = { Car: I.car, Bike: I.bike, Truck: I.truck, EV: I.ev };

  /* ---------- Helpers ---------- */
  const H = {
    esc(s) {
      return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    },
    inr(n) {
      const v = Number(n || 0);
      return '\u20B9' + v.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    initials(name) {
      return (name || '?').trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
    },
    fmtDate(iso) {
      if (!iso) return '-';
      return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    },
    fmtDT(iso) {
      if (!iso) return '-';
      return new Date(iso).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' });
    },
    localDate(d) {
      const p = n => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
    },
    badge(status) {
      const map = {
        reserved: 'badge-warning', confirmed: 'badge-success', active: 'badge-success',
        completed: 'badge-info', cancelled: 'badge-danger', pending: 'badge-warning',
        pending_verification: 'badge-warning', pending_screenshot: 'badge-warning',
        paid: 'badge-success', refunded: 'badge-info', failed: 'badge-danger'
      };
      return map[status] || 'badge-neutral';
    },
    label(status) {
      const map = { pending_verification: 'Awaiting verification' };
      return map[status] || status;
    }
  };

  /* ---------- Protected images ----------
     Screenshots live behind auth, and a bare <img src> only ever sends cookies.
     These helpers load them through API.fetchImage (Bearer header) and swap in
     an object URL, so the admin queue renders even when the cookie is missing. */
  const objectUrls = new Set();

  function releaseObjectUrls() {
    objectUrls.forEach(u => URL.revokeObjectURL(u));
    objectUrls.clear();
  }

  async function mountProtectedImage(img, url) {
    if (!img || !url) return;
    try {
      const objUrl = await API.fetchImage(url);
      objectUrls.add(objUrl);
      if (img.isConnected) img.src = objUrl;
      img.dataset.mounted = '1';
    } catch (e) {
      if (!img.isConnected) return;
      img.dataset.mounted = 'error';
      const wrap = img.closest('.verify-shot') || img.parentElement;
      if (wrap) {
        wrap.innerHTML = `<div class="alert alert-warning" style="margin:0">
          ${I.alert} Screenshot could not be loaded (HTTP ${e.status || 'error'}). Use Refresh to try again.
        </div>`;
      }
    }
  }

  function mountProtectedImages(root) {
    $$('[data-shot-src]', root).forEach(img => mountProtectedImage(img, img.dataset.shotSrc));
  }

  /* ---------- Toast ---------- */
  const Toast = {
    show(message, type = 'info', title = '') {
      const t = document.getElementById('toast-container');
      if (!t) return;
      const icons = { success: I.check, warning: I.tag, danger: I.x, info: I.activity };
      const titles = { success: 'Success', warning: 'Notice', danger: 'Error', info: 'Info' };
      const el = document.createElement('div');
      el.className = `toast toast-${type}`;
      el.setAttribute('role', 'status');
      el.innerHTML = `
        <span class="toast-icon" aria-hidden="true">${icons[type] || icons.info}</span>
        <div class="toast-content">
          <div class="toast-title">${title || titles[type]}</div>
          <div class="toast-message">${H.esc(message)}</div>
        </div>
        <button class="toast-close" aria-label="Dismiss" type="button">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>`;
      t.appendChild(el);
      const kill = () => { el.style.transition = 'all .3s ease'; el.style.opacity = '0'; el.style.transform = 'translateX(30px)'; setTimeout(() => el.remove(), 300); };
      $('.toast-close', el).addEventListener('click', kill);
      setTimeout(kill, 4500);
    },
    success(m) { this.show(m, 'success'); },
    error(m) { this.show(m, 'danger'); },
    warning(m) { this.show(m, 'warning'); }
  };

  /* ---------- Modal ---------- */
  const Modal = {
    open(id) {
      const b = document.getElementById(id);
      if (!b) return;
      b.classList.add('active');
      const m = $('.modal', b);
      if (m) m.classList.add('active');
      document.body.style.overflow = 'hidden';
      const c = $('.modal-close', b);
      if (c) c.focus();
    },
    close(id) {
      const b = document.getElementById(id);
      if (!b) return;
      b.classList.remove('active');
      const m = $('.modal', b);
      if (m) m.classList.remove('active');
      document.body.style.overflow = '';
    },
    closeAll() {
      $$('.modal-backdrop').forEach(b => {
        b.classList.remove('active');
        const m = $('.modal', b);
        if (m) m.classList.remove('active');
      });
      document.body.style.overflow = '';
    }
  };

  /* ---------- Global state ---------- */
  const state = {
    user: null,
    facilitiesPage: 1,
    facility: null,
    slots: [],
    selectedSlots: [],
    price: null,
    draft: null,
    payBooking: null,
    facFilters: { city: '', vehicle_type: '', q: '' },
    userVehicles: [],
    vehicleDrafts: {},
    spareVehicles: [],
    defaultVehicleNo: '',
    pendingRoom: null,
    notifications: [],
    unreadCount: 0,
    pollTimer: null
  };

  /* ============================================================
     NOTIFICATIONS
  ============================================================ */
  const Notifications = {
    TYPE_ICON: {
      payment_verification: I.eye,
      payment_approved: I.check,
      payment_rejected: I.alert
    },

    async load() {
      if (!Auth.isLoggedIn()) return;
      try {
        const res = await API.get('/notifications?limit=25');
        const data = API.ensureOk(res);
        state.notifications = data.notifications || [];
        state.unreadCount = data.unread_count || 0;
        this.render();
      } catch (e) {
        // A failed notification poll must never break the page.
      }
    },

    push(notification) {
      // Socket delivery: prepend and bump the badge without a refetch.
      state.notifications = [notification].concat(state.notifications.filter(
        n => n.id !== notification.id
      )).slice(0, 25);
      if (!notification.is_read) state.unreadCount += 1;
      this.render();
      const type = notification.type || 'info';
      const titles = {
        payment_verification: 'Admin action needed',
        payment_approved: 'Payment approved',
        payment_rejected: 'Payment rejected'
      };
      Toast.show(notification.message || notification.title, type === 'payment_approved' ? 'success' : (type === 'payment_rejected' ? 'danger' : 'warning'), titles[type] || 'Notification');
      // The admin's queue badge should react to a new submission immediately.
      if (notification.type === 'payment_verification' && Auth.user && Auth.user.role === 'admin') {
        const badge = $('[data-verify-count]');
        if (badge) {
          badge.textContent = Number(badge.textContent || 0) + 1;
          badge.classList.remove('d-none');
        }
      }
    },

    render() {
      const btn = $('[data-notif-toggle]');
      if (btn) {
        btn.classList.toggle('has-unread', state.unreadCount > 0);
        const badge = $('[data-notif-count]', btn);
        if (badge) {
          badge.textContent = state.unreadCount > 99 ? '99+' : String(state.unreadCount);
          badge.classList.toggle('d-none', state.unreadCount < 1);
        }
      }

      const list = $('[data-notif-list]');
      if (!list) return;

      const clearBtn = $('[data-notif-clear]');
      if (clearBtn) clearBtn.disabled = !state.notifications.length;
      const markBtn = $('[data-notif-mark-all]');
      if (markBtn) markBtn.disabled = !state.unreadCount;

      if (!state.notifications.length) {
        list.innerHTML = `<div class="notif-empty">${I.inbox}<p>No notifications yet.</p></div>`;
        return;
      }

      list.innerHTML = state.notifications.map(n => {
        const icon = Notifications.TYPE_ICON[n.type] || I.bell;
        return `
          <button type="button" class="notif-item ${n.is_read ? '' : 'unread'}" data-notif-item="${n.id}" data-notif-link="${H.esc(n.link || '')}">
            <span class="notif-icon notif-icon-${H.esc(n.type)}">${icon}</span>
            <span class="notif-body">
              <span class="notif-title">${H.esc(n.title)}</span>
              ${n.message ? `<span class="notif-msg">${H.esc(n.message)}</span>` : ''}
              <span class="notif-time">${H.fmtDT(n.created_at)}</span>
            </span>
            ${n.is_read ? '' : '<span class="notif-dot" aria-label="Unread"></span>'}
          </button>`;
      }).join('');

      $$('[data-notif-item]', list).forEach(b => b.addEventListener('click', () => onNotifClick(b)));
    },

    async markRead(id) {
      const item = state.notifications.find(n => n.id === id);
      if (!item || item.is_read) return;
      item.is_read = true;
      state.unreadCount = Math.max(0, state.unreadCount - 1);
      this.render();
      try {
        const res = await API.put(`/notifications/${id}/read`);
        const data = API.ensureOk(res);
        state.unreadCount = data.unread_count;
        this.render();
      } catch (e) { /* badge is cosmetic; a failure here is not fatal */ }
    },

    async markAllRead() {
      if (!state.unreadCount) return;
      try {
        const data = API.ensureOk(await API.put('/notifications/read-all'));
        state.unreadCount = data.unread_count != null ? data.unread_count : 0;
      } catch (e) {
        // The optimistic update below still clears the badge locally.
      }
      state.notifications.forEach(n => { n.is_read = true; });
      state.unreadCount = 0;
      this.render();
    }
  };

  function toggleNotifPanel(force) {
    const wrap = $('[data-notif]');
    if (!wrap) return;
    const open = force === undefined ? !wrap.classList.contains('open') : force;
    wrap.classList.toggle('open', open);
    const btn = $('[data-notif-toggle]', wrap);
    if (btn) btn.setAttribute('aria-expanded', String(open));
    if (open) Notifications.load();
  }

  async function onNotifClick(btn) {
    const id = Number(btn.dataset.notifItem);
    const link = btn.dataset.notifLink;
    await Notifications.markRead(id);
    if (link) {
      toggleNotifPanel(false);
      if (link === 'admin') {
        navigate('admin');
        adminTab('verifications');
        loadAdminVerifications();
      } else if (link === 'dashboard') {
        navigate('dashboard');
        tab('bookings');
      }
    }
  }

  function resetNotifications() {
    state.notifications = [];
    state.unreadCount = 0;
    Notifications.render();
  }

  /* ============================================================
     NAVIGATION
  ============================================================ */
  function navigate(name) {
    $$('.view').forEach(v => v.classList.remove('active'));
    const target = document.getElementById('view-' + name);
    if (target) target.classList.add('active');
    $('#main').scrollTop = 0;
    window.scrollTo({ top: 0, behavior: 'smooth' });

    $$('.nav-link').forEach(l => l.classList.toggle('active', l.dataset.viewLink === name));
    closeMobileMenu();

    if (name === 'home') loadHome();
    else if (name === 'facilities') loadFacilities();
    else if (name === 'facility' && state.facility) renderFacilityView();
    else if (name === 'dashboard') loadDashboard();
    else if (name === 'admin') loadAdmin();
  }

  function closeMobileMenu() {
    const menu = $('#navbar-menu');
    if (menu) menu.classList.remove('active');
    const tg = $('[data-nav-toggle]');
    if (tg) tg.setAttribute('aria-expanded', 'false');
    
    // Close notification panel too
    const notifWrap = $('[data-notif]');
    if (notifWrap) notifWrap.classList.remove('open');
  }

  /* ============================================================
     NAVBAR AUTH STATE
  ============================================================ */
  function refreshNavbar() {
    const user = Auth.user;
    const guest = $('[data-nav-guest]');
    const ubox = $('[data-nav-user]');
    const dash = $('[data-nav-auth]');
    const admin = $('[data-nav-admin]');
    if (!user) {
      if (guest) guest.classList.remove('d-none');
      if (ubox) ubox.classList.add('d-none');
      if (dash) dash.classList.add('d-none');
      if (admin) admin.classList.add('d-none');
      toggleNotifPanel(false);
      resetNotifications();
      disconnectSocket();
      return;
    }
    if (guest) guest.classList.add('d-none');
    if (ubox) ubox.classList.remove('d-none');
    $$('[data-user-avatar]').forEach(a => { a.textContent = H.initials(user.full_name); });
    const nm = $('[data-user-name]');
    if (nm) nm.textContent = user.full_name.split(' ')[0];
    if (dash) dash.classList.remove('d-none');
    if (admin) admin.classList.toggle('d-none', user.role !== 'admin');
    resetNotifications();
    Notifications.load();
    connectSocket();
  }

  window.AuthChanged = () => { refreshNavbar(); };

/* ============================================================
     HOME
   ============================================================ */
  async function loadHome() {
    // Load hero stats from API
    await loadHeroStats();
    // Load city chips
    try {
      const res = await API.get('/facilities/cities');
      const cities = API.ensureOk(res).cities || [];
      const box = $('#city-chips');
      box.innerHTML = cities.map(c => `<button class="city-chip" data-city="${H.esc(c)}">${H.esc(c)}</button>`).join('');
      $$('.city-chip', box).forEach(b => b.addEventListener('click', () => {
        const sel = $('#fac-city');
        if (sel) sel.value = b.dataset.city;
        state.facFilters.city = b.dataset.city;
        navigate('facilities');
      }));
    } catch (e) { /* non-critical */ }

    // Home search handler
    const homeSearchBtn = $('#home-search-btn');
    const homeSearchInput = $('#home-search');
    if (homeSearchBtn && homeSearchInput) {
      const doSearch = () => {
        const q = homeSearchInput.value.trim();
        if (q) {
          state.facFilters.q = q;
          state.facFilters.city = '';
          navigate('facilities');
        }
      };
      homeSearchBtn.addEventListener('click', doSearch);
      homeSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') doSearch();
      });
    }
  }

  async function loadHeroStats() {
    try {
      // Get all facilities to compute totals
      const res = await API.get('/facilities?per_page=100');
      const data = API.ensureOk(res);
      const facilities = data.facilities || [];
      const cities = [...new Set(facilities.map(f => f.city))].length;

      // Sum all slots
      let totalSlots = 0;
      let totalAvailable = 0;
      facilities.forEach(f => {
        const avail = f.available_slots || {};
        const total = f.total_slots || {};
        Object.values(total).forEach(v => totalSlots += v || 0);
        Object.values(avail).forEach(v => totalAvailable += v || 0);
      });

      // Update hero stats
      $('#hero-stat-cities').textContent = cities;
      $('#hero-stat-facilities').textContent = facilities.length;
      $('#hero-stat-slots').textContent = totalSlots.toLocaleString() + '+';
      $('#hero-stats-badge').querySelector('#hero-stat-cities-label').textContent =
        `${cities} cities \u00B7 ${facilities.length} facilities \u00B7 ${totalSlots.toLocaleString()}+ slots`;

      // Load a featured facility for the hero card (first active one with good availability)
      if (facilities.length) {
        const featured = facilities.find(f => {
          const avail = f.available_slots || {};
          const total = f.total_slots || {};
          let a = 0, t = 0;
          Object.values(avail).forEach(v => a += v || 0);
          Object.values(total).forEach(v => t += v || 0);
          return t > 0 && a / t > 0.1; // at least 10% available
        }) || facilities[0];

        if (featured) {
          $('#hero-facility-name').textContent = featured.name;
          const avail = featured.available_slots || {};
          const total = featured.total_slots || {};
          let a = 0, t = 0;
          Object.values(avail).forEach(v => a += v || 0);
          Object.values(total).forEach(v => t += v || 0);
          const pct = t > 0 ? Math.round((1 - a / t) * 100) : 0;
          $('#hero-availability-text').textContent = `Open now \u00B7 ${a} free slots`;
          $('#hero-occupancy-text').textContent = `${pct}% full`;

          // Load its slots for the mini grid
          try {
            const sRes = await API.get('/facilities/' + featured.id + '/slots');
            const slots = API.ensureOk(sRes).slots || [];
            renderHeroSlotGrid(slots);
          } catch (e) {
            renderHeroSlotGrid([]);
          }
        }
      }
    } catch (e) {
      console.warn('Failed to load hero stats:', e);
      // Fallback to placeholder
      $('#hero-stat-cities').textContent = '-';
      $('#hero-stat-facilities').textContent = '-';
      $('#hero-stat-slots').textContent = '-';
    }
  }

  function renderHeroSlotGrid(slots) {
    const box = $('#hero-slot-grid');
    if (!box) return;
    // Show up to 36 slots, mixed types
    const displaySlots = slots.slice(0, 36);
    let h = '';
    displaySlots.forEach(s => {
      const occupied = s.is_occupied;
      h += `<div class="slot ${occupied ? 'occupied' : ''}" style="cursor:default" tabindex="-1"><span class="slot-code">${H.esc(s.slot_code)}</span></div>`;
    });
    // Fill remaining with placeholders if needed
    for (let i = displaySlots.length; i < 36; i++) {
      h += `<div class="slot occupied" style="cursor:default;opacity:0.3" tabindex="-1"><span class="slot-code">-</span></div>`;
    }
    box.innerHTML = h;
  }

  /* ============================================================
     FACILITIES LISTING
  ============================================================ */
  async function loadFacilities(reset = false) {
    if (reset) state.facilitiesPage = 1;
    const grid = $('#facilities-grid');
    const empty = $('#facilities-empty');
    const pg = $('#facilities-pagination');

    if (!grid) return;

    // City options
    const citySel = $('#fac-city');
    if (!citySel.dataset.ready) {
      citySel.dataset.ready = '1';
      try {
        const res = await API.get('/facilities/cities');
        const cities = API.ensureOk(res).cities || [];
        citySel.innerHTML = '<option value="">All cities</option>' + cities.map(c => `<option value="${H.esc(c)}">${H.esc(c)}</option>`).join('');
      } catch (e) { /* ignore */ }
    }
    citySel.value = state.facFilters.city;
    $('#fac-type').value = state.facFilters.vehicle_type;
    $('#fac-q').value = state.facFilters.q;

    grid.innerHTML = '<div class="loading-state"><span class="loading" aria-label="Loading"></span></div>';
    empty.classList.add('d-none');
    pg.innerHTML = '';

    const params = new URLSearchParams({ page: state.facilitiesPage, per_page: 9 });
    if (state.facFilters.city) params.set('city', state.facFilters.city);
    if (state.facFilters.vehicle_type) params.set('vehicle_type', state.facFilters.vehicle_type);
    if (state.facFilters.q) params.set('q', state.facFilters.q);

    try {
      const res = await API.get('/facilities?' + params.toString());
      const data = API.ensureOk(res);
      const facilities = data.facilities || [];
      grid.innerHTML = '';
      renderFacilityCards(grid, facilities);
      const pages = data.pagination ? data.pagination.pages : 1;
      renderPagination(pg, pages);
      if (!facilities.length) empty.classList.remove('d-none');
    } catch (e) {
      grid.innerHTML = '';
      empty.classList.remove('d-none');
      const p = $('p', empty);
      if (p) p.textContent = 'Unable to load facilities. Please try again.';
    }
  }

  function renderFacilityCards(grid, facilities) {
    if (!facilities.length) { grid.innerHTML = ''; return; }
    grid.innerHTML = facilities.map((f, i) => {
      const avail = f.available_slots || {};
      const total = f.total_slots || {};
      const rates = (f.rates && f.rates.hourly) || {};
      const cls = v => {
        const a = avail[v] || 0, t = total[v] || 0;
        if (!t) return '';
        if (!a) return ' full';
        return (a / t) <= 0.2 ? ' low' : '';
      };
      return `
      <article class="card facility-card animate-fade-in-up list-item-appear" style="animation-delay:${i * 60}ms" data-fid="${f.id}" tabindex="0" role="button" aria-label="${H.esc(f.name)}">
        <div class="facility-card-body">
          <div class="facility-card-top">
            <h3 class="facility-name">${H.esc(f.name)}</h3>
            <span class="facility-rating">${I.star} ${Number(f.rating || 0).toFixed(1)}</span>
          </div>
          <div class="facility-meta">
            <span class="facility-meta-item">${I.pin} ${H.esc(f.area)}, ${H.esc(f.city)} - ${H.esc(f.pincode)}</span>
            <span class="facility-meta-item">${I.clock} ${H.esc(f.open_time || '06:00')} - ${H.esc(f.close_time || '23:00')}</span>
          </div>
          <div class="facility-amenities">
            ${(f.amenities || []).slice(0, 4).map(a => `<span class="amenity-chip">${H.esc(a)}</span>`).join('')}
          </div>
          <div class="facility-availability">
            ${['Car', 'Bike', 'Truck', 'EV'].map(v => `
              <div class="avail-box${cls(v)}">
                <div class="avail-count">${avail[v] || 0}</div>
                <div class="avail-type">${v}s</div>
              </div>`).join('')}
          </div>
          <div class="price-row">
            <span class="price-rate">${H.inr(rates.Car || 40)}<small>/hr (Car)</small></span>
            <span class="btn btn-sm btn-primary">Book Now</span>
          </div>
        </div>
      </article>`;
    }).join('');

    $$('.facility-card', grid).forEach(card => {
      const open = () => openFacility(Number(card.dataset.fid));
      card.addEventListener('click', open);
      card.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
      });
    });
  }

  function renderPagination(container, pages) {
    if (pages <= 1) { container.innerHTML = ''; return; }
    const cur = state.facilitiesPage;
    container.innerHTML = `
      <button class="btn btn-secondary" data-pg-prev ${cur <= 1 ? 'disabled' : ''}>Previous</button>
      <span class="pagination-page">Page ${cur} of ${pages}</span>
      <button class="btn btn-secondary" data-pg-next ${cur >= pages ? 'disabled' : ''}>Next</button>`;
    const on = (sel, fn) => { const b = $(sel, container); if (b && !b.disabled) b.addEventListener('click', fn); };
    on('[data-pg-prev]', () => { state.facilitiesPage--; loadFacilities(); });
    on('[data-pg-next]', () => { state.facilitiesPage++; loadFacilities(); });
  }

  /* ============================================================
     FACILITY DETAIL
  ============================================================ */
  async function openFacility(id) {
    try {
      const [fRes, sRes] = await Promise.all([
        API.get('/facilities/' + id),
        API.get('/facilities/' + id + '/slots')
      ]);
      state.facility = API.ensureOk(fRes).facility;
      state.slots = API.ensureOk(sRes).slots || [];
      state.selectedSlots = [];
      state.price = null;
      resetBookingForm();
      navigate('facility');
    } catch (e) {
      Toast.error('Could not load facility details.');
    }
  }

  function renderFacilityView() {
    const f = state.facility;
    const el = $('#facility-detail-header');
    const avail = f.available_slots || {};
    const total = f.total_slots || {};
    const rates = (f.rates || {});
    const hourly = rates.hourly || {};
    const monthly = rates.monthly || {};
    el.innerHTML = `
      <div class="facility-detail-header">
        <div class="flex-between mb-2" style="align-items:flex-start">
          <div>
            <div class="facility-detail-title">${H.esc(f.name)}</div>
            <div class="detail-meta">
              <span class="detail-meta-item">${I.pin} ${H.esc(f.street)}, ${H.esc(f.area)}, ${H.esc(f.city)} - ${H.esc(f.pincode)}</span>
              <span class="detail-meta-item">${I.clock} ${H.esc(f.open_time || '06:00')} - ${H.esc(f.close_time || '23:00')}</span>
              <span class="facility-rating">${I.star} ${Number(f.rating || 0).toFixed(1)}</span>
            </div>
            ${f.amenities && f.amenities.length ? `<div class="detail-amenities">${f.amenities.map(a => `<span class="amenity-chip">${H.esc(a)}</span>`).join('')}</div>` : ''}
          </div>
          <span class="badge badge-success"><span class="badge-dot"></span>${f.is_active ? 'Open' : 'Closed'}</span>
        </div>
        <div class="divider"></div>
        <div class="grid-4">
          ${['Car', 'Bike', 'Truck', 'EV'].map(v => `
            <div class="avail-box">
              <div class="avail-count">${avail[v] || 0} / ${total[v] || 0}</div>
              <div class="avail-type">${v} slots</div>
            </div>`).join('')}
        </div>
        <table class="rate-table">
          <thead><tr><th></th><th>Car</th><th>Bike</th><th>Truck</th><th>EV</th></tr></thead>
          <tbody>
            <tr><td>Hourly</td>${['Car', 'Bike', 'Truck', 'EV'].map(v => `<td>${H.inr(hourly[v])}</td>`).join('')}</tr>
            <tr><td>Monthly</td>${['Car', 'Bike', 'Truck', 'EV'].map(v => `<td>${H.inr(monthly[v])}</td>`).join('')}</tr>
          </tbody>
        </table>
      </div>`;
    renderSlotGrid();
  }

  function resetBookingForm() {
    const today = new Date();
    const d = $('#booking-date');
    d.min = H.localDate(today);
    d.value = H.localDate(today);
    $('#booking-start').value = '10:00';
    $('#booking-end').value = '12:00';
    $('#booking-slot-count').value = '1';
    $('#booking-vehicle-type').value = 'Car';

    // Drafts are keyed by slot code; a prefilled vehicle goes into the first
    // slot as soon as one is selected.
    state.vehicleDrafts = {};
    state.spareVehicles = [];
    state.defaultVehicleNo = (Auth.user && state.userVehicles && state.userVehicles.length)
      ? ((state.userVehicles.find(v => v.is_default) || state.userVehicles[0]).vehicle_no || '')
      : '';
    renderVehicleInputs();
    renderSlotGrid();
  }

  /* One vehicle number input per selected slot. Drafts are keyed by slot code
     (not by row index) so that deselecting a middle slot keeps the numbers the
     user typed for the slots that remain. */
  function renderVehicleInputs() {
    const box = $('#booking-vehicles-list');
    if (!box) return;
    const codes = state.selectedSlots;

    // Drop drafts whose slot is no longer selected, but remember the numbers so
    // they can be offered back as one-tap suggestions.
    const previous = state.vehicleDrafts || {};
    state.spareVehicles = Object.keys(previous)
      .filter(code => !codes.includes(code))
      .map(code => previous[code])
      .filter(Boolean);

    const drafts = {};
    codes.forEach((code, i) => {
      // First slot picks up the user's default vehicle when nothing is typed yet.
      const seed = previous[code] || (i === 0 && !Object.keys(previous).length ? state.defaultVehicleNo : '');
      drafts[code] = seed || '';
    });
    state.vehicleDrafts = drafts;

    if (!codes.length) {
      box.innerHTML = '<p class="text-muted" style="font-size:0.875rem">Select your slot(s) first, then enter one vehicle number per slot.</p>';
      updateVehicleValidity();
      return;
    }

    const known = (state.userVehicles || []).map(v => v.vehicle_no).filter(Boolean)
      .concat(state.spareVehicles)
      .filter((v, i, arr) => arr.indexOf(v) === i);
    const used = new Set(codes.map(c => drafts[c]).filter(Boolean));

    box.innerHTML = codes.map((code, i) => `
      <div class="vehicle-input-row">
        <span class="vehicle-slot-tag" title="Selected slot">${H.esc(code)}</span>
        <input type="text" class="form-input" data-vehicle-input="${H.esc(code)}"
               aria-label="Vehicle number for slot ${H.esc(code)}"
               placeholder="e.g. MH12AB123${i + 1}" maxlength="15"
               value="${H.esc(drafts[code] || '')}" autocomplete="off">
      </div>`).join('');

    const usable = known.filter(v => !used.has(v));
    if (usable.length) {
      box.insertAdjacentHTML('beforeend', `
        <div class="vehicle-suggestions">
          <span class="text-muted" style="font-size:0.8125rem">Saved:</span>
          ${usable.map(v => `<button type="button" class="chip" data-vehicle-pick="${H.esc(v)}">${H.esc(v)}</button>`).join('')}
        </div>`);
      $$('[data-vehicle-pick]', box).forEach(b => b.addEventListener('click', () => {
        // Fill the first empty row; if all are filled, replace the first.
        const code = codes.find(c => !state.vehicleDrafts[c]) || codes[0];
        state.vehicleDrafts[code] = b.dataset.vehiclePick;
        renderVehicleInputs();
      }));
    }

    $$('[data-vehicle-input]', box).forEach(inp => inp.addEventListener('input', (e) => {
      const code = e.target.dataset.vehicleInput;
      state.vehicleDrafts[code] = e.target.value.toUpperCase();
      e.target.value = state.vehicleDrafts[code];
      updateVehicleValidity();
    }));

    updateVehicleValidity();
  }

  function readVehicleNumbers() {
    return $$('[data-vehicle-input]').map(i => i.value.trim().toUpperCase());
  }

  /* Enforces the 1:1 slot/vehicle rule in the UI so the user sees the problem
     before submitting, and disables the CTA until it is satisfied. */
  function validateVehicles() {
    const need = state.selectedSlots.length;
    const nums = readVehicleNumbers();
    if (!need) return { ok: false, reason: 'Select at least one slot first.', missing: 0 };

    const blanks = nums.filter(v => !v).length;
    if (blanks) {
      return {
        ok: false,
        reason: `Enter a vehicle number for all ${need} selected slot${need > 1 ? 's' : ''} (${blanks} missing).`,
        missing: blanks
      };
    }
    const dupes = nums.filter((v, i) => nums.indexOf(v) !== i);
    if (dupes.length) {
      return { ok: false, reason: `Duplicate vehicle number: ${dupes[0]}. Each slot needs a different vehicle.`, missing: 0 };
    }
    return { ok: true, vehicles: nums, missing: 0 };
  }

  function updateVehicleValidity() {
    const box = $('#booking-vehicles-list');
    const hint = $('#booking-vehicle-hint');
    const cta = $('[data-start-booking]');
    const v = validateVehicles();

    if (hint) {
      if (v.ok) {
        hint.textContent = `${state.selectedSlots.length} slot${state.selectedSlots.length > 1 ? 's' : ''} - ${state.selectedSlots.length} vehicle number${state.selectedSlots.length > 1 ? 's' : ''} entered.`;
        hint.className = 'text-muted';
        hint.style.color = 'var(--color-success)';
        hint.style.fontSize = '0.8125rem';
      } else {
        hint.textContent = v.reason;
        hint.style.color = v.missing ? 'var(--color-warning)' : '';
        hint.style.fontSize = '0.8125rem';
      }
    }
    if (box) box.classList.toggle('invalid', !v.ok && state.selectedSlots.length > 0);
    if (cta && state.selectedSlots.length) cta.disabled = !v.ok;
    return v;
  }

  function getDuration() {
    const start = new Date($('#booking-date').value + 'T' + $('#booking-start').value);
    const end = new Date($('#booking-date').value + 'T' + $('#booking-end').value);
    if (isNaN(start) || isNaN(end) || end <= start) return null;
    const hours = Math.round((end - start) / 3600000);
    if (hours < 1) return null;
    return { start, end, duration_value: hours, duration_unit: 'hours' };
  }

  function renderSlotGrid() {
    const vtype = $('#booking-vehicle-type').value;
    const container = $('#slot-grid-container');
    const available = state.slots
      .filter(s => s.vehicle_type === vtype && !s.is_occupied)
      .sort((a, b) => a.slot_code.localeCompare(b.slot_code, 'en', { numeric: true }));

    if (!available.length) {
      container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">${I.calendar}</div><p>No ${vtype} slots available right now.</p></div>`;
      return;
    }

    const count = parseInt($('#booking-slot-count').value, 10) || 1;
    const limit = Math.min(count, available.length);
    if (state.selectedSlots.length > limit) state.selectedSlots = state.selectedSlots.slice(-limit);

    let html = '<div class="slot-grid">';
    available.forEach(s => {
      const sel = state.selectedSlots.includes(s.slot_code);
      html += `<button type="button" class="slot ${sel ? 'selected' : ''}" data-code="${H.esc(s.slot_code)}"><span class="slot-code">${H.esc(s.slot_code)}</span></button>`;
    });
    html += '</div>';
    html += `<p class="text-muted mt-1" style="font-size:0.8125rem">Select up to ${limit} ${vtype} slot${limit > 1 ? 's' : ''}.</p>`;
    container.innerHTML = html;

    $$('.slot', container).forEach(btn => btn.addEventListener('click', () => {
      const code = btn.dataset.code;
      const i = state.selectedSlots.indexOf(code);
      if (i > -1) state.selectedSlots.splice(i, 1);
      else {
        // Full: drop the oldest pick so the newest click always registers.
        if (state.selectedSlots.length >= limit) state.selectedSlots.shift();
        state.selectedSlots.push(code);
      }
      // renderSlotGrid() ends by re-rendering the vehicle inputs and repricing.
      renderSlotGrid();
    }));

    $('#slot-selected-count-badge').textContent = state.selectedSlots.length + ' selected';
    renderVehicleInputs();
    estimate();
  }

  async function estimate() {
    const f = state.facility;
    if (!f) return;
    const dur = getDuration();
    const cta = $('[data-start-booking]');

    if (!dur) {
      $('#sum-duration').textContent = 'Invalid times';
      if (cta) cta.disabled = true;
      return;
    }
    $('#sum-facility').textContent = f.name;
    $('#sum-duration').textContent = `${dur.duration_value} hour${dur.duration_value > 1 ? 's' : ''}`;

    if (!state.selectedSlots.length) {
      if (cta) cta.disabled = true;
      sumClear();
      return;
    }

    try {
      const res = await API.post('/bookings/price-estimate', {
        facility_id: f.id,
        vehicle_type: $('#booking-vehicle-type').value,
        duration_value: dur.duration_value,
        duration_unit: dur.duration_unit,
        start_time: dur.start.toISOString(),
        slot_count: state.selectedSlots.length
      });
      const p = API.ensureOk(res).price_breakdown;
      state.price = p;
      $('#sum-base').textContent = H.inr(p.base_price);
      if (p.discount) {
        $('#sum-discount').textContent = '-' + H.inr(p.discount);
        $('#sum-discount-label').textContent = 'Discount' + (p.discount_reason ? '' : '');
      } else {
        $('#sum-discount').textContent = '\\u2013';
      }
      $('#sum-gst').textContent = H.inr(p.gst);
      $('#sum-total').textContent = H.inr(p.total_amount);
    } catch (e) {
      sumClear();
      if (cta) cta.disabled = true;
      return;
    }

    // Price is settled; the CTA now depends only on the vehicle numbers.
    const v = updateVehicleValidity();
    if (cta) cta.disabled = !v.ok;
  }

  function sumClear() {
    ['#sum-base', '#sum-discount', '#sum-gst', '#sum-total'].forEach(s => {
      const el = $(s);
      if (el) el.textContent = '\u2013';
    });
  }

  /* ============================================================
     BOOKING
  ============================================================ */
  function openBookingModal() {
    const f = state.facility;
    if (!f) return;
    const dur = getDuration();
    if (!dur) { Toast.error('Please set a valid time range.'); return; }
    if (!state.selectedSlots.length) { Toast.error('Please select at least one slot.'); return; }

    // One vehicle number per selected slot, enforced before anything is sent.
    const vehicleCheck = validateVehicles();
    if (!vehicleCheck.ok) { Toast.error(vehicleCheck.reason); return; }

    if (!state.price) { Toast.error('Could not compute price. Try again.'); return; }

    const vehicleNos = vehicleCheck.vehicles;
    state.draft = {
      facility_id: f.id,
      vehicle_nos: vehicleNos,
      vehicle_no: vehicleNos[0],
      vehicle_type: $('#booking-vehicle-type').value,
      start_time: dur.start.toISOString(),
      end_time: dur.end.toISOString(),
      duration_value: dur.duration_value,
      duration_unit: dur.duration_unit,
      slot_codes: state.selectedSlots.slice()
    };
    const p = state.price;
    const box = $('#booking-modal-content');
    box.innerHTML = `
      <div class="alert alert-info demo-banner" style="margin-bottom:var(--spacing-md);background:rgba(74,144,217,0.1);border-color:var(--color-secondary);color:var(--color-secondary);display:flex;align-items:center;gap:var(--spacing-sm)">
        <span>${I.shield}</span>
        <strong>Demo Mode:</strong> Booking will be created but payment is simulated. No real money is charged.
      </div>
      <div class="summary-item"><span class="label">Facility</span><span class="value">${H.esc(f.name)}</span></div>
      <div class="summary-item"><span class="label">Slots</span><span class="value">${state.selectedSlots.map(s => `<span class="badge badge-info" style="margin:2px">${H.esc(s)}</span>`).join(' ')}</span></div>
      <div class="summary-item"><span class="label">Start</span><span class="value">${H.fmtDT(dur.start.toISOString())}</span></div>
      <div class="summary-item"><span class="label">End</span><span class="value">${H.fmtDT(dur.end.toISOString())}</span></div>
      <div class="divider"></div>
      <div class="form-label mb-2">Vehicle${state.selectedSlots.length > 1 ? 's' : ''} for this booking</div>
      ${state.selectedSlots.map((code, i) => `
        <div class="summary-item"><span class="label">${H.esc(code)}</span><span class="value"><strong>${H.esc(vehicleNos[i])}</strong> &middot; ${H.esc(state.draft.vehicle_type)}</span></div>`).join('')}
      <div class="divider"></div>
      <div class="summary-item"><span class="label">Base price</span><span class="value">${H.inr(p.base_price)}</span></div>
      ${p.discount ? `<div class="summary-item discount"><span class="label">Discount</span><span class="value">-${H.inr(p.discount)}</span></div>` : ''}
      <div class="summary-item"><span class="label">GST (18%)</span><span class="value">${H.inr(p.gst)}</span></div>
      <div class="summary-item total"><span class="label">Total payable</span><span class="value">${H.inr(p.total_amount)}</span></div>`;
    Modal.open('booking-modal');
  }

  async function confirmBooking() {
    if (!state.draft) return;
    const btn = $('#booking-confirm-btn');
    btn.disabled = true; btn.textContent = 'Creating booking...';
    try {
      const res = await API.post('/bookings', state.draft);
      const booking = API.ensureOk(res).booking;
      Modal.close('booking-modal');
      btn.disabled = false; btn.textContent = 'Confirm & Proceed to Pay';
      Toast.success('Booking created! Complete payment to confirm.');
      // Release the slots the user was holding on this form.
      state.selectedSlots = [];
      state.vehicleDrafts = {};
      state.spareVehicles = [];
      renderSlotGrid();
      openPayment(booking);
    } catch (e) {
      const info = API.handleError({ status: e && e.status, data: e && e.data });
      Toast.error(info.message || 'Failed to create booking.');
      btn.disabled = false; btn.textContent = 'Confirm & Proceed to Pay';
    }
  }

/* ============================================================
     PAYMENT
   ============================================================ */
  let socket = null;

  function initSocket() {
    if (typeof io === 'undefined') return null;
    if (socket) return socket;
    const s = io({ transports: ['websocket', 'polling'], auth: { token: API.userStore.token } });
    s.on('connect', () => {
      // Rooms do not survive a drop, so re-subscribe on every (re)connect.
      const room = state.pendingRoom || (state.payBooking && state.payBooking.id);
      if (room) {
        s.emit('join_booking', { booking_id: room });
        state.pendingRoom = null;
      }
    });
    s.on('connect_error', (err) => {
      // An expired token makes the server reject the handshake. Notifications
      // still work through REST polling, so just refresh silently.
      if (Auth.isLoggedIn()) {
        API.userStore.token && API.get('/notifications/unread-count').then(() => {});
      }
    });
    s.on('notification', (data) => {
      if (data) Notifications.push(data);
    });
    s.on('notification_admin', () => {
      // Badge only: the real notification arrives on the per-user `notification`
      // event, and the queue is refreshed when the Verifications tab is opened.
      if (Auth.user && Auth.user.role === 'admin') loadAdminVerifications(true);
    });
    s.on('payment_paid', (data) => {
      if (state.payBooking && state.payBooking.id === data.booking_id) {
        showSuccess(data);
      }
      Toast.success('Payment successful!');
    });
    s.on('booking_updated', (data) => {
      if (data.status === 'confirmed' && data.payment_status === 'paid') {
        Toast.success('Payment approved! Your slot is confirmed.');
        if (state.payBooking && state.payBooking.id === data.id) {
          showSuccess({ transaction_id: data.transaction_id, paid_at: data.paid_at });
        }
      } else if (data.status === 'cancelled' && data.payment_status === 'failed') {
        Toast.error('Payment rejected. Your booking has been cancelled.');
        Modal.closeAll();
      }
      if (Auth.isLoggedIn() && $$('[data-dash-panel="bookings"].active').length) {
        loadUserBookings();
      }
    });
    s.on('payment_failed', (data) => {
      if (state.payBooking && state.payBooking.id === data.booking_id) {
        $('#payment-status').innerHTML = `<div class="alert alert-danger mt-2">Payment failed: ${H.esc(data.gateway_response || 'Please try again')}</div>`;
        const btn = $('#pay-now-btn');
        if (btn) { btn.disabled = false; btn.textContent = 'Try Again'; }
      }
      Toast.error('Payment failed. Please try again.');
    });
    s.on('payment_screenshot_uploaded', () => {
      if (state.payBooking) renderPendingVerification();
    });
    return s;
  }

  function connectSocket() {
    if (!Auth.isLoggedIn()) return;
    if (!socket) socket = initSocket();
    // A token refresh or a re-login means a fresh token must be presented.
    if (socket) {
      socket.auth = { token: API.userStore.token };
      if (!socket.connected) socket.connect();
    }
  }

  function disconnectSocket() {
    if (!socket) return;
    socket.disconnect();
    socket = null;
  }

  function joinBookingRoom(bookingId) {
    if (!bookingId) return;
    if (socket && socket.connected) {
      socket.emit('join_booking', { booking_id: bookingId });
    } else {
      // Not connected yet (first open, or a reconnect in flight). The connect
      // handler re-joins from state.payBooking, so nothing is lost.
      state.pendingRoom = bookingId;
    }
  }

  function leaveBookingRoom(bookingId) {
    if (bookingId) state.pendingRoom = null;
    if (socket && socket.connected) {
      socket.emit('leave_booking', { booking_id: bookingId });
    }
  }

  function openPayment(booking) {
    state.payBooking = booking;
    state.upiQrData = null;
    state.screenshotBase64 = null;
    connectSocket();
    joinBookingRoom(booking.id);

    // A screenshot is already with the admin: show the waiting state instead of
    // letting the user upload a second copy.
    if (booking.payment_status === 'pending_verification') {
      // Clear the footer so the stale "Pay" button cannot be reused.
      const pFooter = $('.modal-footer', $('#payment-modal'));
      if (pFooter) pFooter.innerHTML = '<button class="btn btn-secondary" data-modal-close>Close</button>';
      const closeBtn = $('[data-modal-close]', pFooter);
      if (closeBtn) closeBtn.addEventListener('click', () => Modal.close('payment-modal'));
      renderPendingVerification();
      Modal.open('payment-modal');
      return;
    }

    const box = $('#payment-modal-content');
    box.innerHTML = `
      <div class="mb-3">
        <div class="summary-item"><span class="label">Booking</span><span class="value confirm-code">${H.esc(booking.booking_id)}</span></div>
        <div class="summary-item"><span class="label">Amount due</span><span class="value" style="font-size:1.375rem;font-weight:700;color:var(--color-primary)">${H.inr(booking.total_amount)}</span></div>
      </div>
      <label class="form-label">Choose payment method</label>
      <div class="payment-methods mb-3">
        <button type="button" class="payment-method selected" data-method="upi">${I.ev} UPI</button>
        <button type="button" class="payment-method" data-method="wallet">${I.wallet} Wallet</button>
      </div>
      <div id="upi-qr-container" style="display:none"></div>
      <div id="payment-status"></div>`;

    const st = $('#payment-status');
    const qrContainer = $('#upi-qr-container');

    function setFooter(method) {
      const footer = $('.modal-footer', $('#payment-modal'));
      if (method === 'wallet') {
        footer.innerHTML = `
          <button class="btn btn-secondary" data-modal-close>Cancel</button>
          <button class="btn btn-accent" id="pay-now-btn">Pay ${H.inr(booking.total_amount)}</button>`;
        $('#pay-now-btn').addEventListener('click', initiatePayment);
      } else {
        // UPI is completed from the card itself (screenshot + submit), so the
        // footer only offers a way out.
        footer.innerHTML = '<button class="btn btn-secondary" data-modal-close>Close</button>';
      }
      const closeBtn = $('[data-modal-close]', footer);
      if (closeBtn) closeBtn.addEventListener('click', () => Modal.close('payment-modal'));
    }

    $$('.payment-method', box).forEach(b => b.addEventListener('click', () => {
      $$('.payment-method', box).forEach(x => x.classList.remove('selected'));
      b.classList.add('selected');
      const method = b.dataset.method;

      if (method === 'wallet') {
        qrContainer.style.display = 'none';
        st.innerHTML = '<div class="alert alert-info mt-2 demo-banner" style="background:rgba(74,144,217,0.1);border-color:var(--color-secondary);color:var(--color-secondary);display:flex;align-items:center;gap:var(--spacing-sm)"><span>${I.shield}</span><strong>Demo Mode:</strong> Wallet payment is simulated. No real money is deducted.</div>';
      } else {
        qrContainer.style.display = 'block';
        st.innerHTML = '';
        if (!state.upiQrData) loadUpiQr(booking);
      }
      setFooter(method);
    }));

    setFooter('upi');
    Modal.open('payment-modal');

    // Auto-load UPI QR since it's the default selected
    setTimeout(() => loadUpiQr(booking), 100);
  }

  async function loadUpiQr(booking) {
    try {
      const res = await API.post('/payments/upi/qr', { booking_id: booking.id });
      const data = API.ensureOk(res);
      state.upiQrData = data;
      renderUpiPayment(booking, data);
    } catch (e) {
      $('#upi-qr-container').innerHTML = '<div class="alert alert-danger">Failed to load UPI QR. Please try again.</div>';
    }
  }

  function renderUpiPayment(booking, qrData) {
    const container = $('#upi-qr-container');
    const p = qrData.pricing || {};
    const slots = (booking.slot_codes && booking.slot_codes.length) ? booking.slot_codes : ['-'];
    const vehicles = (booking.vehicles && booking.vehicles.length) ? booking.vehicles : [booking.vehicle_no];
    const upiId = qrData.merchant_upi || '';
    const duration = durationLabel(booking.duration_value, booking.duration_unit);

    container.innerHTML = `
      <div class="alert alert-info demo-banner" style="margin-bottom:var(--spacing-md);background:rgba(74,144,217,0.1);border-color:var(--color-secondary);color:var(--color-secondary);display:flex;align-items:center;gap:var(--spacing-sm)">
        <span>${I.shield}</span>
        <strong>Demo Mode:</strong> Payment is simulated. No real money is charged. Use any UPI ID and upload a test screenshot for admin verification.
      </div>
      <div class="upi-card">
        <div class="upi-card-head">
          <span class="upi-head-icon" aria-hidden="true">${I.wallet}</span>
          <h3 id="upi-pay-heading">UPI Payment</h3>
        </div>

        <div class="upi-note">
          <span class="upi-note-line">${I.ev} Scan the QR code below and make the payment using any UPI app</span>
          <span class="upi-note-line">${I.shield} After payment, upload the screenshot and enter the transaction ID for verification.</span>
        </div>

        <div class="upi-grid">
          <section class="upi-panel" aria-labelledby="upi-qr-heading">
            <h4 class="upi-panel-title" id="upi-qr-heading">${I.ev} Scan &amp; Pay</h4>
            <div class="upi-qr-wrap">
              <img class="upi-qr" src="${qrData.qr_code}" alt="UPI QR code to pay ${H.esc(H.inr(qrData.amount))} for booking ${H.esc(booking.booking_id)}" width="240" height="240">
              <div class="upi-qr-label">Scan &amp; Pay</div>
              <div class="upi-qr-id">UPI ID: ${H.esc(upiId)}</div>
              <button type="button" class="upi-copy" id="upi-copy-btn">${I.copy} Copy UPI ID</button>
            </div>

            <div class="upi-booking-box">
              <div class="upi-booking-row">
                <span class="label">Parking Slot</span>
                <span class="value">${H.esc(slots.join(', '))}</span>
              </div>
              <div class="upi-booking-row">
                <span class="label">Vehicle Number</span>
                <span class="value">${H.esc(vehicles.join(', '))}</span>
              </div>
              <div class="upi-booking-row">
                <span class="label">Duration</span>
                <span class="value">${H.esc(duration)}</span>
              </div>
              <div class="upi-booking-row">
                <span class="label">Date &amp; Time</span>
                <span class="value">${H.esc(fmtPayDT(booking.start_time))}</span>
              </div>
              <div class="upi-booking-row amount">
                <span class="label">Amount to Pay</span>
                <span class="value">${H.inr(qrData.amount)}</span>
              </div>
              <div class="upi-booking-note">${H.esc(rateBreakdown(p, duration))}</div>
            </div>
          </section>

          <section class="upi-panel" aria-labelledby="upi-upload-heading">
            <h4 class="upi-panel-title" id="upi-upload-heading">${I.upload} Upload Payment Screenshot</h4>

            <div class="upi-drop" id="upi-drop" role="button" tabindex="0"
                 aria-describedby="upi-drop-meta">
              <span class="upi-drop-icon" aria-hidden="true">${I.cloudUpload}</span>
              <div class="upi-drop-title">Click to upload</div>
              <div class="upi-drop-hint">or drag and drop</div>
              <div class="upi-drop-meta" id="upi-drop-meta">PNG, JPG, or JPEG (Max 5MB)</div>
              <input type="file" id="upi-file" accept="image/png,image/jpeg" hidden>
            </div>

            <div class="upi-field">
              <label class="form-label" for="upi-txn-id">Transaction ID</label>
              <input type="text" id="upi-txn-id" class="form-input" inputmode="numeric" autocomplete="off"
                     placeholder="Enter UPI Transaction ID (e.g. 1234567890)">
            </div>

            <div class="upi-field">
              <button type="button" class="btn btn-primary btn-lg upi-submit" id="upi-submit-btn" disabled>
                ${I.check} Submit for Verification
              </button>
              <p class="upi-footnote">An admin verifies your payment and you are notified once it is approved.</p>
            </div>
          </section>
        </div>
      </div>`;

    const copyBtn = $('#upi-copy-btn', container);
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(upiId);
        Parkease.showToast('UPI ID copied!', 'success');
      } catch (e) {
        Toast.error('Could not copy. Please note the UPI ID manually.');
      }
    });

    bindUpiDrop(booking);
  }

  /* "2 hours" -> "2 Hours" / "1 month" -> "1 Month" */
  function durationLabel(value, unit) {
    const labels = { hours: 'Hour', days: 'Day', monthly: 'Month' };
    const one = labels[unit] || unit || 'Hour';
    return `${value} ${value === 1 ? one : one + 's'}`;
  }

  /* Shows why the amount is what it is: the rate for the slot type, times the time. */
  function rateBreakdown(p, duration) {
    if (!p.rate) return 'Amount depends on slot type and booking duration';
    const parts = [`${H.inr(p.rate)}/${p.rate_basis === 'monthly' ? 'month' : 'hour'} x ${duration}`];
    if (p.slot_count > 1) parts.push(`${p.slot_count} slots`);
    if (p.discount > 0) parts.push(`discount -${H.inr(p.discount)}`);
    parts.push(`GST +${H.inr(p.gst)}`);
    return parts.join(' | ');
  }

  /* "02 Oct 2026, 10:00 AM" */
  function fmtPayDT(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    if (isNaN(d)) return '-';
    const date = d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    const time = d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
    return `${date}, ${time}`.replace(/\s?(am|pm)$/i, (m) => ' ' + m.toUpperCase());
  }

  function bindUpiDrop(booking) {
    const drop = $('#upi-drop');
    const fileInput = $('#upi-file');
    const submitBtn = $('#upi-submit-btn');

    function accept(file) {
      if (!file) return;
      const allowed = ['image/png', 'image/jpeg'];
      if (allowed.indexOf(file.type) === -1) {
        Toast.error('Please upload a PNG, JPG or JPEG image');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        Toast.error('File too large. Max 5MB.');
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        state.screenshotBase64 = e.target.result;
        drop.classList.add('has-file');
        drop.innerHTML = `
          <img class="upi-preview" src="${e.target.result}" alt="Selected payment screenshot preview">
          <div class="upi-preview-name">${H.esc(file.name)}</div>
          <div class="upi-drop-hint" style="margin-top:var(--spacing-xs)">Click to choose a different file</div>`;
        drop.appendChild(fileInput);
        submitBtn.disabled = false;
      };
      reader.onerror = () => { state.screenshotBase64 = null; submitBtn.disabled = true; Toast.error('Could not read that file. Try another.'); };
      reader.readAsDataURL(file);
    }

    drop.addEventListener('click', () => fileInput.click());
    drop.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); }
    });
    drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('dragging'); });
    drop.addEventListener('dragleave', () => drop.classList.remove('dragging'));
    drop.addEventListener('drop', (e) => {
      e.preventDefault();
      drop.classList.remove('dragging');
      if (e.dataTransfer.files[0]) accept(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
      if (e.target.files[0]) accept(e.target.files[0]);
    });

    submitBtn.addEventListener('click', async () => {
      const transactionId = $('#upi-txn-id').value.trim();
      if (!state.screenshotBase64) {
        Toast.error('Please upload your payment screenshot');
        return;
      }
      submitBtn.disabled = true;
      submitBtn.innerHTML = `${I.refresh} Submitting...`;
      try {
        const res = await API.post('/payments/upi/upload-screenshot', {
          booking_id: booking.id,
          screenshot_base64: state.screenshotBase64,
          transaction_id: transactionId
        });
        API.ensureOk(res);
        renderPendingVerification();
      } catch (err) {
        const info = API.handleError({ status: err && err.status, data: err && err.data });
        Toast.error(info.message);
        submitBtn.disabled = false;
        submitBtn.innerHTML = `${I.check} Submit for Verification`;
      }
    });
  }

  function renderPendingVerification() {
    const box = $('#payment-modal-content');
    if (!box || !state.payBooking) return;
    const booking = state.payBooking;
    box.innerHTML = `
      <div class="pending-verify">
        <div class="pending-verify-icon">${I.shield}</div>
        <h3>Payment under verification</h3>
        <p class="text-muted mb-3">
          We have received your screenshot for booking <strong>${H.esc(booking.booking_id)}</strong>.
          An admin will check it and you'll be notified as soon as it is approved.
        </p>
        <div class="summary-item"><span class="label">Amount</span><span class="value">${H.inr(booking.total_amount)}</span></div>
        <div class="summary-item"><span class="label">Status</span><span class="value"><span class="badge badge-warning">Awaiting verification</span></span></div>
        <div class="mt-3" style="display:flex;gap:var(--spacing-sm);justify-content:center">
          <button class="btn btn-primary" id="pending-check-btn">${I.refresh} Check status</button>
          <button class="btn btn-secondary" id="pending-done-btn">Close</button>
        </div>
      </div>`;
    const check = $('#pending-check-btn');
    if (check) check.addEventListener('click', () => checkPaymentStatus(booking.id, true));
    const done = $('#pending-done-btn');
    if (done) done.addEventListener('click', () => {
      Modal.closeAll();
      if (Auth.isLoggedIn()) navigate('dashboard');
    });
    startPaymentPolling(booking.id);
  }

  /* Poll as a safety net. The socket is the primary channel, but if the tab was
     closed, offline, or the socket dropped, this still catches the decision. */
  function startPaymentPolling(bookingId) {
    if (state.pollTimer) clearInterval(state.pollTimer);
    let ticks = 0;
    state.pollTimer = setInterval(async () => {
      ticks += 1;
      if (ticks > 120) { clearInterval(state.pollTimer); state.pollTimer = null; return; }
      const resolved = await checkPaymentStatus(bookingId, false);
      if (resolved) { clearInterval(state.pollTimer); state.pollTimer = null; }
    }, 5000);
    checkPaymentStatus(bookingId, false);
  }

  async function checkPaymentStatus(bookingId, manual) {
    try {
      const res = await API.get(`/payments/status/${bookingId}`);
      const data = API.ensureOk(res);
      const paymentStatus = data.payment ? data.payment.status : data.payment_status;

      if (paymentStatus === 'paid') {
        if (state.pollTimer) { clearInterval(state.pollTimer); state.pollTimer = null; }
        Modal.closeAll();
        showSuccess({
          transaction_id: (data.payment && data.payment.transaction_id) || '',
          paid_at: new Date().toISOString()
        });
        if (manual) Parkease.showToast('Payment approved!', 'success');
        loadUserBookings();
        return true;
      }
      if (paymentStatus === 'failed') {
        if (state.pollTimer) { clearInterval(state.pollTimer); state.pollTimer = null; }
        Modal.closeAll();
        Toast.error('Payment rejected. Your booking has been cancelled.');
        if (manual) Toast.error('Payment rejected.');
        loadUserBookings();
        return true;
      }
      if (manual) Parkease.showToast('Still waiting for the admin to review your payment.', 'warning');
      return false;
    } catch (e) {
      if (manual) Toast.error('Could not check payment status.');
      return false;
    }
  }

  async function initiatePayment() {
    const booking = state.payBooking;
    if (!booking) return;
    const sel = $('.payment-method.selected');
    const method = sel ? sel.dataset.method : 'wallet';
    const btn = $('#pay-now-btn');
    btn.disabled = true; btn.textContent = 'Processing...';

    try {
      const res = await API.post('/payments/initiate', { booking_id: booking.id, payment_method: method });
      const data = API.ensureOk(res);
      if (data.payment.status === 'paid') {
        showSuccess(data.payment);
        leaveBookingRoom(booking.id);
        return;
      }
      $('#payment-status').innerHTML = `<div class="empty-state" style="padding:var(--spacing-lg)"><span class="loading" aria-label="Processing"></span><p class="mt-2">Waiting for payment confirmation... (check your payment app)</p></div>`;
      // Real-time updates will come via WebSocket
    } catch (e) {
      const info = API.handleError({ status: e && e.status, data: e && e.data });
      $('#payment-status').innerHTML = `<div class="alert alert-danger mt-2">${H.esc(info.message)}</div>`;
      btn.disabled = false; btn.textContent = 'Try Again';
    }
  }

  function showSuccess(payment) {
    const booking = state.payBooking;
    const body = $('#success-modal-body');
    body.innerHTML = `
      <div class="qr-box">
        <div style="width:72px;height:72px;margin:0 auto var(--spacing-md);border-radius:50%;background:rgba(0,201,167,.12);display:flex;align-items:center;justify-content:center;color:var(--color-accent-dark)">${I.check}</div>
        <h3 style="font-size:1.375rem;margin-bottom:var(--spacing-xs)">Payment successful!</h3>
        <p class="text-muted mb-3">Transaction ${H.esc(payment.transaction_id || '')} <br>${H.fmtDT(payment.paid_at)}</p>
        <div class="confirm-code">${H.esc(booking.booking_id)}</div>
        <p class="mt-2">Show this code at the facility gate to check in.</p>
        <div style="display:flex;gap:var(--spacing-sm);justify-content:center;margin-top:var(--spacing-md)">
          <button class="btn btn-outline btn-sm" data-dl-receipt>Download Receipt</button>
          <button class="btn btn-primary btn-sm" data-go-dash>Go to Dashboard</button>
        </div>
      </div>`;
    Modal.closeAll();
    Modal.open('success-modal');
    const dl = $('[data-dl-receipt]');
    if (dl) dl.addEventListener('click', () => { window.open('/api/bookings/' + booking.id + '/receipt', '_blank'); });
    const gd = $('[data-go-dash]');
    if (gd) gd.addEventListener('click', () => { Modal.close('success-modal'); if (Auth.isLoggedIn()) navigate('dashboard'); else navigate('home'); });
  }

  /* ============================================================
     DASHBOARD
  ============================================================ */
  function tab(name) {
    $$('[data-dash-tab]').forEach(b => b.classList.toggle('active', b.dataset.dashTab === name));
    $$('[data-dash-panel]').forEach(p => p.classList.toggle('active', p.dataset.dashPanel === name));
    if (name === 'bookings') loadUserBookings();
    if (name === 'vehicles') loadUserVehicles();
    if (name === 'payments') loadPayments();
    if (name === 'profile') renderProfile();
  }

  async function loadDashboard() {
    const user = Auth.user;
    if (!user) { navigate('login'); return; }

    $$('[data-user-avatar]').forEach(a => a.textContent = H.initials(user.full_name));
    const nm = $('[data-user-name-full]'); if (nm) nm.textContent = user.full_name;
    const em = $('[data-user-email]'); if (em) em.textContent = user.email;
    const gr = $('#dash-greeting');
    if (gr) {
      const h = new Date().getHours();
      gr.textContent = (h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening') + ', ' + user.full_name.split(' ')[0] + '!';
    }
    const as = $('[data-admin-sidebar]');
    if (as) as.classList.toggle('d-none', user.role !== 'admin');

    // Load vehicles for prefilling
    try { const r = await API.get('/users/vehicles'); state.userVehicles = API.ensureOk(r).vehicles || []; }
    catch (e) { state.userVehicles = []; }

    tab('bookings');
  }

  async function loadUserBookings() {
    const box = $('#dashboard-bookings');
    if (!box) return;
    box.innerHTML = '<div class="loading-state"><span class="loading" aria-label="Loading"></span></div>';
    try {
      const res = await API.get('/users/bookings?per_page=100');
      const list = API.ensureOk(res).bookings || [];
      if (!list.length) {
        box.innerHTML = `<div class="card"><div class="empty-state"><div class="empty-state-icon">${I.calendar}</div><h3>No bookings yet</h3><p>Find a parking spot and make your first booking.</p><button class="btn btn-primary" data-go-fac>Find Parking</button></div></div>`;
        const b = $('[data-go-fac]', box);
        if (b) b.addEventListener('click', () => navigate('facilities'));
        return;
      }
      box.innerHTML = list.map(b => `
        <div class="card mb-2">
          <div class="card-body">
            <div class="flex-between mb-1" style="align-items:flex-start">
              <div>
                <div class="confirm-code" style="font-size:1.0625rem">${H.esc(b.booking_id)}</div>
                <div class="text-muted" style="font-size:.8125rem">Booked ${H.fmtDT(b.created_at)}</div>
              </div>
              <span class="badge ${H.badge(b.status)}">${H.esc(b.status)}</span>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:var(--spacing-md);margin:var(--spacing-sm) 0;font-size:.9375rem">
              <span>${((b.vehicles && b.vehicles.length) ? b.vehicles : [b.vehicle_no])
                .map(v => `<strong>${H.esc(v)}</strong>`).join(' &middot; ')} &middot; ${H.esc(b.vehicle_type)}</span>
              <span class="text-muted">${H.fmtDT(b.start_time)} &rarr; ${H.fmtDT(b.end_time)}</span>
            </div>
            ${b.payment_status === 'pending_verification' ? `
              <div class="alert alert-warning" style="margin:var(--spacing-sm) 0;font-size:.8125rem">
                ${I.shield} Payment screenshot submitted and awaiting admin verification.
                <button class="btn btn-sm btn-outline" data-recheck="${b.id}">Check status</button>
              </div>` : ''}
            <div class="flex-between" style="align-items:center">
              <span style="font-weight:700;color:var(--color-primary)">${H.inr(b.total_amount)}</span>
              <span class="table-actions">
                <span class="badge ${H.badge(b.payment_status)}">${H.esc(b.payment_status)}</span>
                ${b.payment_status === 'pending_verification' ? `<button class="btn btn-sm btn-primary" data-repay="${b.id}">View payment</button>` : ''}
                ${b.payment_status === 'paid' && ['reserved', 'confirmed'].includes(b.status) ? `<button class="btn btn-sm btn-outline" data-checkin="${b.id}">Check in</button>` : ''}
                ${b.status === 'active' ? `<button class="btn btn-sm btn-primary" data-checkout="${b.id}">Check out</button>` : ''}
                ${['reserved', 'confirmed', 'active'].includes(b.status) ? `<button class="btn btn-sm btn-danger" data-cancel="${b.id}">Cancel</button>` : ''}
                ${b.check_in_time ? `<a class="btn btn-sm btn-secondary" href="/api/bookings/${b.id}/receipt" target="_blank">Receipt</a>` : ''}
              </span>
            </div>
          </div>
        </div>`).join('');

      $$('[data-checkin]', box).forEach(b => b.addEventListener('click', () => checkIn(Number(b.dataset.checkin))));
      $$('[data-checkout]', box).forEach(b => b.addEventListener('click', () => checkOut(Number(b.dataset.checkout))));
      $$('[data-cancel]', box).forEach(b => b.addEventListener('click', () => cancelBooking(Number(b.dataset.cancel))));
      $$('[data-recheck]', box).forEach(b => b.addEventListener('click', () => checkPaymentStatus(Number(b.dataset.recheck), true)));
      // Re-open the payment modal so a user can see the pending state or retry
      // if their earlier upload was never received.
      $$('[data-repay]', box).forEach(b => b.addEventListener('click', () => {
        const booking = list.find(x => String(x.id) === b.dataset.repay);
        if (booking) openPayment(booking);
      }));

      scheduleLifecycleRefresh(list);
    } catch (e) {
      box.innerHTML = '<div class="empty-state"><p>Could not load your bookings.</p></div>';
    }
  }

  async function checkIn(id) {
    try {
      await API.post(`/bookings/${id}/checkin`);
      Toast.success('Checked in! Enjoy your stay.');
      loadUserBookings();
    } catch (e) {
      const info = API.handleError({ status: e && e.status, data: e && e.data });
      Toast.error(info.message);
    }
  }

  async function checkOut(id) {
    try {
      await API.post(`/bookings/${id}/checkout`);
      Toast.success('Checked out. Your slot is free again.');
      loadUserBookings();
    } catch (e) {
      const info = API.handleError({ status: e && e.status, data: e && e.data });
      Toast.error(info.message);
    }
  }

  /* A checked-in booking completes itself once its end time passes, but the
     list on screen would otherwise keep showing it as active until a manual
     reload. Re-fetch shortly after the nearest end time so the flip to
     "completed" appears on its own. */
  let lifecycleTimer = null;

  function scheduleLifecycleRefresh(list) {
    if (lifecycleTimer) { clearTimeout(lifecycleTimer); lifecycleTimer = null; }

    const ends = (list || [])
      .filter(b => b.status === 'active' && b.end_time)
      .map(b => new Date(b.end_time).getTime() - Date.now())
      .filter(ms => Number.isFinite(ms));

    if (!ends.length) return;

    // Wake just after the soonest end time. Capped so a long stay still
    // re-checks periodically instead of sleeping for hours.
    const wait = Math.min(Math.max(Math.min(...ends) + 5000, 5000), 10 * 60 * 1000);
    lifecycleTimer = setTimeout(() => {
      lifecycleTimer = null;
      if (document.visibilityState === 'visible') loadUserBookings();
      else scheduleLifecycleRefresh(list);
    }, wait);
  }

  async function cancelBooking(id) {
    if (!confirm('Cancel this booking? Refunds may apply per policy.')) return;
    try {
      await API.del('/bookings/' + id);
      Toast.success('Booking cancelled.');
      loadUserBookings();
      loadPayments();
    } catch (e) {
      const info = API.handleError({ status: e && e.status, data: e && e.data });
      Toast.error(info.message);
    }
  }

  async function loadUserVehicles() {
    const box = $('#dashboard-vehicles');
    if (!box) return;
    box.innerHTML = '<div class="loading-state"><span class="loading" aria-label="Loading"></span></div>';
    try {
      const res = await API.get('/users/vehicles');
      const list = API.ensureOk(res).vehicles || [];
      state.userVehicles = list;
      if (!list.length) {
        box.innerHTML = `<div class="card"><div class="empty-state"><div class="empty-state-icon">${I.car}</div><h3>No vehicles added</h3><p>Add your vehicle to book faster.</p><button class="btn btn-primary" data-add-veh>Add Vehicle</button></div></div>`;
        const b = $('[data-add-veh]', box);
        if (b) b.addEventListener('click', () => openVehicleModal());
        return;
      }
      box.innerHTML = `<div class="grid-2">` + list.map(v => `
        <div class="card">
          <div class="card-body">
            <div class="flex-between mb-1">
              <h3 style="font-size:1.125rem">${H.esc(v.vehicle_no)}</h3>
              ${v.is_default ? '<span class="badge badge-success">Default</span>' : ''}
            </div>
            <p class="text-muted mb-3">${H.esc(v.vehicle_type)}</p>
            <span class="table-actions">
              ${!v.is_default ? `<button class="btn btn-sm btn-outline" data-setdef="${v.id}">Make default</button>` : ''}
              <button class="icon-btn danger touch-target" data-delveh="${v.id}" aria-label="Remove vehicle">${I.x}</button>
            </span>
          </div>
        </div>`).join('') + `</div>`;
      $$('[data-setdef]', box).forEach(b => b.addEventListener('click', async () => {
        try { await API.put(`/users/vehicles/${b.dataset.setdef}/default`); Toast.success('Default vehicle updated.'); loadUserVehicles(); }
        catch (err) { Toast.error('Could not update.'); }
      }));
      $$('[data-delveh]', box).forEach(b => b.addEventListener('click', async () => {
        if (!confirm('Remove this vehicle?')) return;
        try { await API.del('/users/vehicles/' + b.dataset.delveh); Toast.success('Vehicle removed.'); loadUserVehicles(); }
        catch (err) { Toast.error('Could not remove.'); }
      }));
    } catch (e) {
      box.innerHTML = '<div class="empty-state"><p>Could not load vehicles.</p></div>';
    }
  }

  function openVehicleModal() {
    $('#vehicle-no').value = '';
    $('#vehicle-type').value = 'Car';
    $('#vehicle-default').checked = false;
    Modal.open('vehicle-modal');
    $('#vehicle-no').focus();
  }

  async function saveVehicle() {
    const no = $('#vehicle-no').value.trim().toUpperCase();
    if (!no) { Toast.error('Vehicle number is required.'); return; }
    const btn = $('#vehicle-save-btn');
    btn.disabled = true;
    try {
      const res = await API.post('/users/vehicles', {
        vehicle_no: no,
        vehicle_type: $('#vehicle-type').value,
        is_default: $('#vehicle-default').checked
      });
      API.ensureOk(res);
      Modal.close('vehicle-modal');
      Toast.success('Vehicle added.');
      loadUserVehicles();
    } catch (e) {
      const info = API.handleError({ status: e && e.status, data: e && e.data });
      Toast.error(info.message);
    }
    btn.disabled = false;
  }

  async function loadPayments() {
    const box = $('#dashboard-payments');
    if (!box) return;
    box.innerHTML = '<div class="loading-state"><span class="loading" aria-label="Loading"></span></div>';
    try {
      const [hist, wall] = await Promise.all([
        API.get('/payments/history'),
        API.get('/payments/wallet')
      ]);
      const list = API.ensureOk(hist).payments || [];
      const balance = API.ensureOk(wall).wallet_balance || 0;
      let html = `
        <div class="card mb-3">
          <div class="card-body flex-between" style="align-items:center">
            <div>
              <div class="text-muted">Wallet balance</div>
              <div style="font-size:1.875rem;font-weight:700;color:var(--color-accent-dark)">${H.inr(balance)}</div>
            </div>
            <button class="btn btn-accent" data-wallet-topup>+ Add Money</button>
          </div>
        </div>`;
      if (!list.length) {
        html += `<div class="card"><div class="empty-state"><div class="empty-state-icon">${I.wallet}</div><h3>No transactions yet</h3><p>Your payment history will appear here.</p></div></div>`;
      } else {
        html += `<div class="table-responsive"><table class="data-table">
          <thead><tr><th>Booking</th><th>Transaction</th><th>Amount</th><th>Method</th><th>Status</th><th>Date</th></tr></thead>
          <tbody>` + list.map(p => `
            <tr>
              <td>${H.esc(p.booking_id)}</td>
              <td>${H.esc(p.transaction_id || '-')}</td>
              <td>${H.inr(p.amount)}</td>
              <td>${H.esc(p.method || '-')}</td>
              <td><span class="badge ${H.badge(p.status)}">${H.esc(p.status)}</span></td>
              <td>${H.fmtDT(p.paid_at)}</td>
            </tr>`).join('') + `</tbody></table></div>`;
      }
      box.innerHTML = html;
      const tp = $('[data-wallet-topup]', box);
      if (tp) tp.addEventListener('click', () => addMoney(balance));
    } catch (e) {
      box.innerHTML = '<div class="empty-state"><p>Could not load payments.</p></div>';
    }
  }

  function addMoney(balance) {
    const amt = prompt('Enter amount to add to wallet (max \u20B950,000):');
    if (!amt) return;
    const n = Number(amt);
    if (isNaN(n) || n <= 0 || n > 50000) { Toast.error('Invalid amount (1-50000).'); return; }
    (async () => {
      try {
        const res = await API.post('/payments/wallet/add', { amount: n });
        const data = API.ensureOk(res);
        Toast.success('Wallet topped up. New balance: ' + H.inr(data.wallet_balance));
        loadPayments();
      } catch (e) {
        const info = API.handleError({ status: e && e.status, data: e && e.data });
        Toast.error(info.message);
      }
    })();
  }

  function renderProfile() {
    const u = Auth.user;
    const box = $('#dashboard-profile');
    if (!u) return;
    box.innerHTML = `
      <div class="card" style="max-width:560px">
        <div class="card-body">
          <form id="profile-form">
            <div class="form-group">
              <label class="form-label" for="p-name">Full name</label>
              <input type="text" id="p-name" class="form-input" value="${H.esc(u.full_name)}">
            </div>
            <div class="form-group">
              <label class="form-label" for="p-phone">Mobile number</label>
              <input type="tel" id="p-phone" class="form-input" maxlength="10" value="${H.esc(u.phone || '')}">
            </div>
            <div class="form-group">
              <label class="form-label">Email (cannot change)</label>
              <input type="text" class="form-input" value="${H.esc(u.email)}" disabled>
            </div>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </form>
          <div class="divider"></div>
          <h3 style="font-size:1.0625rem;margin-bottom:var(--spacing-md)">Change password</h3>
          <form id="pwd-form">
            <div class="form-group"><label class="form-label" for="pwd-current">Current password</label><input type="password" id="pwd-current" class="form-input" autocomplete="current-password"></div>
            <div class="form-group"><label class="form-label" for="pwd-new">New password</label><input type="password" id="pwd-new" class="form-input" autocomplete="new-password"><span class="password-hint">Min 8 chars, 1 uppercase, 1 number, 1 special char.</span></div>
            <button type="submit" class="btn btn-outline">Update Password</button>
          </form>
        </div>
      </div>`;

    $('#profile-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const res = await API.put('/users/profile', { full_name: $('#p-name').value.trim(), phone: $('#p-phone').value.trim() });
        const us = API.ensureOk(res).user;
        API.userStore.user = us;
        state.user = us;
        refreshNavbar();
        Toast.success('Profile updated.');
        loadDashboard();
      } catch (err) {
        const info = API.handleError({ status: err && err.status, data: err && err.data });
        Toast.error(info.message);
      }
    });
    $('#pwd-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await API.put('/auth/change-password', { current_password: $('#pwd-current').value, new_password: $('#pwd-new').value });
        $('#pwd-current').value = ''; $('#pwd-new').value = '';
        Toast.success('Password updated.');
      } catch (err) {
        const info = API.handleError({ status: err && err.status, data: err && err.data });
        Toast.error(info.message);
      }
    });
  }

  /* ============================================================
     ADMIN
  ============================================================ */
async function loadAdmin() {
    const user = Auth.user;
    if (!user || user.role !== 'admin') { navigate('dashboard'); return; }
    adminTab('verifications');
    loadAdminStats();
    loadAdminVerifications();
    loadAdminBookings();
    loadAdminUsers();
    loadAdminFacilities();
    loadAdminRevenue();
  }

  function adminTab(name) {
    $$('[data-admin-tab]').forEach(b => b.classList.toggle('active', b.dataset.adminTab === name));
    $$('[data-admin-panel]').forEach(p => p.classList.toggle('active', p.dataset.adminPanel === name));
    if (name === 'verifications') loadAdminVerifications();
    if (name === 'bookings') loadAdminBookings();
    if (name === 'users') loadAdminUsers();
    if (name === 'facilities') loadAdminFacilities();
    if (name === 'revenue') loadAdminRevenue();
  }

  /* ---------- Verification queue ---------- */
  let lastQueueSignature = null;
  async function loadAdminVerifications(quiet) {
    const box = $('#admin-verifications-body');
    if (!box) return;
    // On a socket-triggered refresh keep the current cards on screen so the
    // admin does not lose their place or a half-open review.
    if (!quiet) box.innerHTML = '<div class="loading-state"><span class="loading" aria-label="Loading"></span></div>';
    try {
      const res = await API.get('/admin/payments/pending');
      const data = API.ensureOk(res);
      const items = data.verifications || [];

      const count = $('[data-verify-count]');
      if (count) {
        count.textContent = items.length;
        count.classList.toggle('d-none', items.length < 1);
      }

      // A quiet refresh exists only to surface new uploads. If the set of
      // payments is unchanged, leave the DOM (and its loaded images) alone.
      const signature = items.map(i => i.payment_id + ':' + (i.screenshot_file || '')).join('|');
      if (quiet && signature === lastQueueSignature && box.children.length) return;
      lastQueueSignature = signature;

      if (!items.length) {
        box.innerHTML = `<div class="empty-state"><div class="empty-state-icon">${I.shield}</div><h3>Nothing to verify</h3><p>No payment screenshots are waiting for review.</p></div>`;
        return;
      }

      box.innerHTML = `<div class="alert alert-info">${I.alert} <strong>${items.length}</strong> payment${items.length > 1 ? 's' : ''} awaiting your decision. Check each screenshot against the amount due before approving.</div>` +
        items.map(v => `
        <div class="verify-card">
          <div class="verify-card-head">
            <div>
              <div class="confirm-code" style="font-size:1rem">${H.esc(v.booking.booking_id)}</div>
              <div class="text-muted" style="font-size:0.8125rem">
                ${H.esc(v.user ? v.user.full_name : 'Unknown user')} &middot; ${H.esc(v.user ? v.user.user_id : '')}
                &middot; uploaded ${H.fmtDT(v.uploaded_at)}
              </div>
            </div>
            <div style="text-align:right">
              <div style="font-size:1.25rem;font-weight:700;color:var(--color-primary)">${H.inr(v.amount)}</div>
              <div class="text-muted" style="font-size:0.8125rem">Amount due</div>
            </div>
          </div>
          <div class="verify-card-body">
            <div class="verify-meta">
              <div><span class="label">Vehicle${(v.booking.vehicles || []).length > 1 ? 's' : ''}</span><span class="value">${(v.booking.vehicles || []).map(x => H.esc(x)).join(', ') || H.esc(v.booking.vehicle_no)}</span></div>
              <div><span class="label">Slots</span><span class="value">${(v.booking.slot_codes || []).map(s => `<span class="badge badge-info">${H.esc(s)}</span>`).join(' ')}</span></div>
              <div><span class="label">Period</span><span class="value">${H.fmtDT(v.booking.start_time)} &rarr; ${H.fmtDT(v.booking.end_time)}</span></div>
              <div><span class="label">Transaction ID</span><span class="value" style="font-family:var(--font-mono);font-size:.8125rem">${H.esc(v.transaction_id) || '<span class="text-muted">Not provided</span>'}</span></div>
            </div>
            <div class="verify-shot">
              ${v.screenshot_url
                ? `<img alt="Payment screenshot for ${H.esc(v.booking.booking_id)}" data-shot-src="${H.esc(v.screenshot_url)}" data-shot="${v.payment_id}">
                   <button type="button" class="btn btn-secondary btn-sm mt-2" data-shot-open="${v.payment_id}">${I.eye} Open full size</button>`
                : '<div class="text-muted" style="padding:var(--spacing-lg);text-align:center">No screenshot was attached.</div>'}
            </div>
          </div>
          <div class="verify-card-foot">
            <button class="btn btn-primary btn-sm" data-verify-open="${v.payment_id}">${I.shield} Review &amp; decide</button>
          </div>
        </div>`).join('');

      releaseObjectUrls();
      mountProtectedImages(box);

      $$('[data-verify-open]', box).forEach(b => b.addEventListener('click', () => openVerifyScreenshot(b.dataset.verifyOpen)));
      $$('[data-shot-open]', box).forEach(b => {
        const img = $(`[data-shot="${b.dataset.shotOpen}"]`, box);
        if (!img) return;
        b.addEventListener('click', async () => {
          // The blob may still be loading; wait for it so the tab is never blank.
          if (!img.src) await mountProtectedImage(img, img.dataset.shotSrc);
          if (img.src) window.open(img.src, '_blank');
        });
      });
    } catch (e) {
      box.innerHTML = '<div class="empty-state"><p>Could not load the verification queue.</p></div>';
    }
  }

  async function loadAdminStats() {
	    const box = $('#admin-stats');
	    if (!box) return;
	    box.innerHTML = '<div class="loading-state"><span class="loading" aria-label="Loading"></span></div>';
	    try {
	      const res = await API.get('/admin/dashboard');
	      const d = API.ensureOk(res);
	      const s = d.stats || {};
	      box.innerHTML = `
	        <div class="card stat-card"><div class="stat-icon">${I.users}</div><div><div class="stat-value">${s.total_users || 0}</div><div class="stat-label">Total users</div></div></div>
	        <div class="card stat-card"><div class="stat-icon green">${I.pin}</div><div><div class="stat-value">${s.total_facilities || 0}</div><div class="stat-label">Active facilities</div></div></div>
	        <div class="card stat-card"><div class="stat-icon amber">${I.calendar}</div><div><div class="stat-value">${s.total_bookings || 0}</div><div class="stat-label">Total bookings</div></div></div>
        <div class="card stat-card"><div class="stat-icon red">${I.activity}</div><div><div class="stat-value">${s.today_revenue || 0}</div><div class="stat-label">Today&apos;s revenue</div></div></div>`;
      const badge = $('[data-verify-count]');
      if (badge) {
        badge.textContent = s.pending_verifications || 0;
        badge.classList.toggle('d-none', !s.pending_verifications);
      }
    } catch (e) {
	      box.innerHTML = '<div class="card stat-card"><div><div class="stat-label">Could not load stats.</div></div></div>';
	    }
	  }
	
async function loadAdminBookings() {
    const body = $('#admin-bookings-body');
    const footer = $('#admin-bookings-footer');
    if (!body) return;
    body.innerHTML = `<tr><td colspan="7"><div class="loading-state"><span class="loading" aria-label="Loading"></span></div></td></tr>`;
    const status = $('#admin-booking-status').value;
    const params = new URLSearchParams({ per_page: 50 });
    if (status) params.set('status', status);
    try {
      const res = await API.get('/admin/bookings?' + params);
      const list = API.ensureOk(res).bookings || [];
      body.innerHTML = list.map(b => {
        const vehicles = (b.vehicles && b.vehicles.length) ? b.vehicles : [b.vehicle_no];
        // The action column links into the same review modal the Verifications
        // tab uses, so pass the booking id and let it resolve the payment.
        const verifyBtn = b.payment_status === 'pending_verification'
          ? `<button class="btn btn-sm btn-primary" data-verify-screenshot="${b.id}">${I.shield} Verify</button>`
          : '';
        const receiptBtn = b.payment_status === 'paid'
          ? `<a class="btn btn-sm btn-secondary" href="/api/bookings/${b.id}/receipt" target="_blank">Receipt</a>`
          : '';
        return `
        <tr>
          <td><strong>${H.esc(b.booking_id)}</strong></td>
          <td>#${b.user_id}</td>
          <td>#${b.facility_id}</td>
          <td>${vehicles.map(v => H.esc(v)).join('<br>')} <span class="text-muted">(${H.esc(b.vehicle_type)})</span></td>
          <td>${H.inr(b.total_amount)}</td>
          <td><span class="badge ${H.badge(b.status)}">${H.esc(b.status)}</span> <span class="badge ${H.badge(b.payment_status)} mt-1">${H.esc(b.payment_status)}</span></td>
          <td>${verifyBtn} ${receiptBtn}</td>
        </tr>`;
      }).join('') || `<tr><td colspan="7"><div class="empty-state"><p>No bookings.</p></div></td></tr>`;
      
      $$('[data-verify-screenshot]', body).forEach(b => b.addEventListener('click', () => openVerifyScreenshot(b.dataset.verifyScreenshot)));
footer.innerHTML = `<span class="pagination-page">${list.length} bookings shown</span>`;
    } catch (e) {
      body.innerHTML = `<tr><td colspan="7"><div class="empty-state"><p>Could not load bookings.</p></div></td></tr>`;
    }
  }

  async function openVerifyScreenshot(ref) {
    try {
      const res = await API.get('/admin/payments/pending');
      const items = API.ensureOk(res).verifications || [];
      // Callers pass a payment id (Verifications tab) or a booking id
      // (bookings table); accept either.
      const item = items.find(v => String(v.payment_id) === String(ref))
        || items.find(v => String(v.booking.id) === String(ref));
      if (!item) return Toast.error('This payment is no longer awaiting verification');

      const booking = item.booking;
      const user = item.user;

      const body = $('#success-modal-body');
      body.innerHTML = `
        <div class="modal-head-simple">
          <h3>${I.shield} Verify UPI payment</h3>
          <p class="text-muted">Compare the screenshot against the amount due, then approve or reject.</p>
        </div>
        <div class="verify-modal-grid">
          <div class="card" style="padding:var(--spacing-md)">
            <div class="summary-item"><span class="label">Booking</span><span class="value confirm-code">${H.esc(booking.booking_id)}</span></div>
            <div class="summary-item"><span class="label">Amount due</span><span class="value" style="font-weight:700">${H.inr(item.amount)}</span></div>
            <div class="summary-item"><span class="label">Paid via</span><span class="value">${H.esc(String(item.method || '').toUpperCase())}</span></div>
            <div class="summary-item"><span class="label">User</span><span class="value">${H.esc(user ? user.full_name : 'Unknown')} <span class="text-muted">(${H.esc(user ? user.user_id : '')})</span></span></div>
            <div class="summary-item"><span class="label">Contact</span><span class="value" style="font-size:.8125rem">${H.esc(user ? user.email : '')}</span></div>
            <div class="summary-item"><span class="label">Vehicle${(booking.vehicles || []).length > 1 ? 's' : ''}</span><span class="value">${(booking.vehicles || []).map(x => H.esc(x)).join(', ') || H.esc(booking.vehicle_no)}</span></div>
            <div class="summary-item"><span class="label">Slots</span><span class="value">${(booking.slot_codes || []).map(s => `<span class="badge badge-info">${H.esc(s)}</span>`).join(' ')}</span></div>
            <div class="summary-item"><span class="label">Period</span><span class="value" style="font-size:.8125rem">${H.fmtDT(booking.start_time)} &rarr; ${H.fmtDT(booking.end_time)}</span></div>
            <div class="summary-item"><span class="label">Transaction ID</span><span class="value" style="font-family:var(--font-mono);font-size:.8125rem">${H.esc(item.transaction_id) || 'Not provided'}</span></div>
            <div class="summary-item"><span class="label">Uploaded</span><span class="value">${H.fmtDT(item.uploaded_at)}</span></div>
          </div>
          <div class="card" style="padding:var(--spacing-md);text-align:center">
            <label class="form-label" style="display:block;text-align:left">Payment Screenshot</label>
            ${item.screenshot_url ? `
              <img alt="Payment screenshot" style="max-width:100%;max-height:420px;border:1px solid var(--color-border);border-radius:var(--radius-md);cursor:zoom-in" data-verify-shot data-shot-src="${H.esc(item.screenshot_url)}">
              <p class="text-muted small mt-1">Click the image to open it full size</p>
            ` : '<p class="text-muted">No screenshot available</p>'}
          </div>
        </div>
        <div class="form-group mt-3">
          <label class="form-label" for="admin-verify-notes">Notes (required when rejecting)</label>
          <textarea id="admin-verify-notes" class="form-input" rows="3" placeholder="e.g. Amount on screenshot does not match, or Verified against bank statement."></textarea>
        </div>
        <div style="display:flex;gap:var(--spacing-sm)">
          <button class="btn btn-danger btn-flex-1" id="btn-reject">${I.x} Reject payment</button>
          <button class="btn btn-success btn-flex-1" id="btn-approve">${I.check} Approve payment</button>
        </div>`;

      Modal.closeAll();
      Modal.open('success-modal');

      const shot = $('[data-verify-shot]', body);
      mountProtectedImage(shot, shot && shot.dataset.shotSrc);
      if (shot) shot.addEventListener('click', async () => {
        if (!shot.src) await mountProtectedImage(shot, shot.dataset.shotSrc);
        if (shot.src) window.open(shot.src, '_blank');
      });

      const approve = $('#btn-approve');
      const reject = $('#btn-reject');
      approve.addEventListener('click', async () => {
        approve.disabled = true; reject.disabled = true;
        await verifyScreenshotAction(item.payment_id, 'approve', $('#admin-verify-notes').value.trim());
      });
      reject.addEventListener('click', async () => {
        const notes = $('#admin-verify-notes').value.trim();
        if (!notes) {
          Toast.error('Please add a note explaining the rejection');
          $('#admin-verify-notes').focus();
          return;
        }
        reject.disabled = true; approve.disabled = true;
        await verifyScreenshotAction(item.payment_id, 'reject', notes);
      });
    } catch (e) {
      Toast.error('Failed to load the payment for review');
    }
  }

  async function verifyScreenshotAction(paymentId, action, notes) {
    try {
      const res = await API.post(`/payments/admin/verify-screenshot/${paymentId}`, { action, notes });
      API.ensureOk(res);
      Parkease.showToast(
        action === 'approve' ? 'Payment approved and booking confirmed' : 'Payment rejected and booking cancelled',
        action === 'approve' ? 'success' : 'warning'
      );
      Modal.close('success-modal');
      loadAdminVerifications();
      loadAdminBookings();
      loadAdminStats();
    } catch (e) {
      const info = API.handleError({ status: e && e.status, data: e && e.data });
      Toast.error(info.message);
      const approve = $('#btn-approve');
      const reject = $('#btn-reject');
      if (approve) approve.disabled = false;
      if (reject) reject.disabled = false;
    }
  }

  async function loadAdminUsers() {
	    const body = $('#admin-users-body');
	    if (!body) return;
	    body.innerHTML = `<tr><td colspan="7"><div class="loading-state"><span class="loading" aria-label="Loading"></span></div></tr></td></tr>`;
	    try {
	      const res = await API.get('/admin/users?per_page=50');
	      const list = API.ensureOk(res).users || [];
	      body.innerHTML = list.map(u => `
	        <tr>
	          <td><strong>${H.esc(u.full_name)}</strong><br><span class="text-muted" style="font-size:.8125rem">${H.esc(u.email)}</span></td>
	          <td>${H.esc(u.user_id)}</td>
	          <td>${H.esc(u.phone)}</td>
	          <td><span class="badge ${u.role === 'admin' ? 'badge-danger' : 'badge-info'}">${H.esc(u.role)}</span></td>
	          <td>${H.inr(u.wallet_balance)}</td>
	          <td><span class="badge ${u.is_blocked ? 'badge-danger' : 'badge-success'}">${u.is_blocked ? 'Blocked' : 'Active'}</span></td>
	          <td>${u.role !== 'admin' ? `<button class="btn btn-sm ${u.is_blocked ? 'btn-outline' : 'btn-danger'}" data-block="${u.id}">${u.is_blocked ? 'Unblock' : 'Block'}</button>` : ''}</td>
	        </tr>`).join('') || `<tr><td colspan="7"><div class="empty-state"><p>No users.</p></div></td></tr>`;
	      $$('[data-block]', body).forEach(b => b.addEventListener('click', async () => {
	        try {
	          const res = await API.put(`/admin/users/${b.dataset.block}/block`);
	          const nu = API.ensureOk(res).user;
	          Toast.success(nu.is_blocked ? 'User blocked.' : 'User unblocked.');
	          loadAdminUsers();
	        } catch (e) {
	          Toast.error('Could not update user.');
	        }
	      }));
	    } catch (e) {
	      body.innerHTML = `<tr><td colspan="7"><div class="empty-state"><p>Could not load users.</p></div></td></tr>`;
	    }
	  }
	
	  async function loadAdminFacilities() {
	    const body = $('#admin-facilities-body');
	    if (!body) return;
	    body.innerHTML = `<tr><td colspan="7"><div class="loading-state"><span class="loading" aria-label="Loading"></span></div></td></tr>`;
	    try {
	      const res = await API.get('/admin/facilities');
	      const list = API.ensureOk(res).facilities || [];
	      body.innerHTML = list.map(f => {
	        const avail = f.available_slots || {}, total = f.total_slots || {};
	        return `
	        <tr>
	          <td><strong>${H.esc(f.name)}</strong></td>
	          <td>${H.esc(f.city)}</td>
	          <td>${Object.values(total).reduce((a, b) => a + (b || 0), 0)}</td>
	          <td>${Object.values(avail).reduce((a, b) => a + (b || 0), 0)}</td>
	          <td>${Number(f.rating || 0).toFixed(1)}</td>
	          <td><span class="badge ${f.is_active ? 'badge-success' : 'badge-neutral'}">${f.is_active ? 'Active' : 'Inactive'}</span></td>
	          <td><a class="btn btn-sm btn-outline" href="#" data-view-fac="${f.id}">View</a></td>
	        </tr>`;
	      }).join('') || `<tr><td colspan="7"><div class="empty-state"><p>No facilities.</p></div></td></tr>`;
	    } catch (e) {
	      body.innerHTML = `<tr><td colspan="7"><div class="empty-state"><p>Could not load facilities.</p></div></td></tr>`;
	    }
	  }
	
	  async function loadAdminRevenue() {
	    const box = $('#revenue-breakdown');
	    const top = $('#top-facilities');
	    if (!box) return;
	    try {
	      const res = await API.get('/admin/revenue?days=30');
	      const d = API.ensureOk(res);
	      const total = (d.daily || []).reduce((a, x) => a + (x.revenue || 0), 0);
	      const bv = d.by_vehicle || [];
	      box.innerHTML = `
	        <div class="card stat-card"><div class="stat-icon green">${I.activity}</div><div><div class="stat-value">${H.inr(total)}</div><div class="stat-label">30-day revenue</div></div></div>
	        <div class="card"><div class="card-body"><h4 class="mb-2" style="font-size:.9375rem">By vehicle type</h4>${bv.map(v => `
	          <div class="mb-2"><div class="flex-between mb-1"><span style="font-size:.8125rem">${H.esc(v.vehicle_type)}</span><span style="font-size:.8125rem">${H.inr(v.revenue)}</span></div>
	          <div class="progress-track"><div class="progress-fill" style="width:${total ? Math.round(v.revenue / total * 100) : 0}%"></div></div></div>`).join('') || '<p class="text-muted">No data</p>'}</div></div>
	        <div class="card"><div class="card-body"><h4 class="mb-2" style="font-size:.9375rem">Bookings / day</h4>${(d.daily || []).slice(-7).map(x => `
	          <div class="mb-2"><div class="flex-between mb-1"><span style="font-size:.8125rem">${H.esc(x.date)}</span><span style="font-size:.8125rem">${x.bookings} bkgs</span></div>
	          <div class="progress-track"><div class="progress-fill green" style="width:${x.bookings * 10}%"></div></div></div>`).join('') || '<p class="text-muted">No data</p>'}</div></div>`;
	      top.innerHTML = `<div class="table-responsive"><table class="data-table">
	        <thead><tr><th>Facility</th><th>Revenue</th><th>Bookings</th></tr></thead>
	        <tbody>` + (d.top_facilities || []).map(f => `
	          <tr><td>${H.esc(f.name)}</td><td>${H.inr(f.revenue)}</td><td>${f.bookings}</td></tr>`).join('') +
	        `</tbody></table></div>`;
	    } catch (e) {
	      box.innerHTML = '<div class="card"><div class="card-body"><p class="text-muted">Revenue data unavailable.</p></div></div>';
	    }
	  }
	
	  function openFacilityModal() {
	    ['fac-name', 'fac-street', 'fac-area', 'fac-city-in', 'fac-pincode', 'fac-lat', 'fac-lng'].forEach(id => {
	      const el = document.getElementById(id);
	      if (el) el.value = '';
	    });
	    $('#fac-total-car').value = 20; $('#fac-total-bike').value = 30;
	    $('#fac-total-truck').value = 5; $('#fac-total-ev').value = 5;
	    Modal.open('facility-modal');
	    $('#fac-name').focus();
	  }
	
	  async function saveFacility() {
	    const val = id => { const e = document.getElementById(id); return e ? e.value.trim() : ''; };
	    const name = val('fac-name');
	    if (!name) { Toast.error('Facility name required.'); return; }
	    const btn = $('#facility-save-btn');
	    btn.disabled = true;
	    try {
	      const res = await API.post('/facilities', {
	        name,
	        street: val('fac-street'),
	        area: val('fac-area'),
	        city: val('fac-city-in'),
	        pincode: val('fac-pincode'),
	        latitude: Number(val('fac-lat')),
	        longitude: Number(val('fac-lng')),
	        total_car: Number($('#fac-total-car').value),
	        total_bike: Number($('#fac-total-bike').value),
	        total_truck: Number($('#fac-total-truck').value),
	        total_ev: Number($('#fac-total-ev').value)
	      });
	      API.ensureOk(res);
	      Modal.close('facility-modal');
	      Toast.success('Facility created!');
	      loadAdminFacilities();
	    } catch (e) {
	      const info = API.handleError({ status: e && e.status, data: e && e.data });
	      Toast.error(info.message);
	    }
	    btn.disabled = false;
	  }

  /* ============================================================
     AUTH FORMS
  ============================================================ */
  function bindAuth() {
    $('#login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = $('#login-email').value.trim();
      const pass = $('#login-password').value;
      if (!email || !pass) { Toast.error('Please enter your email and password.'); return; }
      const btn = $('button[type=submit]', e.target);
      btn.disabled = true; btn.textContent = 'Signing in...';
      try {
        const res = await API.post('/auth/login', { email, password: pass });
        const data = API.ensureOk(res);
        Auth.saveSession(data);
        Toast.success('Welcome back, ' + (data.user.full_name || '') + '!');
        navigate(data.user.role === 'admin' ? 'admin' : 'home');
      } catch (err) {
        const info = API.handleError({ status: err && err.status, data: err && err.data });
        Toast.error(info.message);
      }
      btn.disabled = false; btn.textContent = 'Sign In';
    });

    $('#register-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const f = {
        full_name: $('#reg-name').value.trim(),
        email: $('#reg-email').value.trim(),
        phone: $('#reg-phone').value.trim(),
        password: $('#reg-password').value,
        vehicle_no: $('#reg-vehicle').value.trim().toUpperCase() || undefined
      };
      if (!f.full_name || !f.email || !f.phone || !f.password) { Toast.error('Please fill all required fields.'); return; }
      const btn = $('button[type=submit]', e.target);
      btn.disabled = true; btn.textContent = 'Creating account...';
      try {
        const res = await API.post('/auth/register', f);
        const data = API.ensureOk(res);
        Auth.saveSession(data);
        if (f.vehicle_no) {
          try { await API.post('/users/vehicles', { vehicle_no: f.vehicle_no, vehicle_type: 'Car', is_default: true }); } catch (x) { /* optional */ }
        }
        Toast.success('Account created! Welcome to ParkEase.');
        navigate('dashboard');
      } catch (err) {
        const info = API.handleError({ status: err && err.status, data: err && err.data });
        Toast.error(info.message);
      }
      btn.disabled = false; btn.textContent = 'Create Account';
    });
  }

  /* ============================================================
     GLOBAL EVENT BINDING & INIT
  ============================================================ */
  function bindGlobal() {
    // View links
    $$('[data-view-link]').forEach(el => {
      el.addEventListener('click', (e) => {
        if (el.tagName === 'A' && el.getAttribute('href') === '#') e.preventDefault();
        navigate(el.dataset.viewLink);
      });
    });

    // Brand
    $$('.navbar-brand').forEach(el => el.addEventListener('click', e => { e.preventDefault(); navigate('home'); }));

    // Mobile toggle
    const tg = $('[data-nav-toggle]');
    if (tg) tg.addEventListener('click', () => {
      const menu = $('#navbar-menu');
      const open = menu.classList.toggle('active');
      tg.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    // Logout
    const lo = $('[data-nav-logout]');
    if (lo) lo.addEventListener('click', () => { Auth.logout(); Toast.success('Logged out.'); navigate('home'); state.user = null; });

    // Home search
    const hs = $('[data-home-search]');
    const hi = $('#home-search');
    const doSearch = () => {
      const q = (hi.value || '').trim();
      state.facFilters.q = q;
      state.facFilters.city = '';
      navigate('facilities');
    };
    if (hs) hs.addEventListener('click', doSearch);
    if (hi) hi.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });

    // Facility filters
    const af = $('[data-facilities-apply]');
    if (af) af.addEventListener('click', () => {
      state.facFilters.city = $('#fac-city').value;
      state.facFilters.vehicle_type = $('#fac-type').value;
      state.facFilters.q = $('#fac-q').value.trim();
      loadFacilities(true);
    });
    const rf = $('[data-facilities-reset]');
    if (rf) rf.addEventListener('click', () => {
      state.facFilters = { city: '', vehicle_type: '', q: '' };
      loadFacilities(true);
    });

    // Facility detail controls
    const vt = $('#booking-vehicle-type');
    if (vt) vt.addEventListener('change', () => { state.selectedSlots = []; renderSlotGrid(); });
    const sc = $('#booking-slot-count');
    if (sc) sc.addEventListener('change', () => { state.selectedSlots = state.selectedSlots.slice(0, Number(sc.value)); renderSlotGrid(); });
    ['booking-date', 'booking-start', 'booking-end'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', () => { if (state.facility) { state.selectedSlots = []; renderSlotGrid(); } });
    });

    // Booking CTA
    const sbb = $('[data-start-booking]');
    if (sbb) sbb.addEventListener('click', () => {
      if (!Auth.isLoggedIn()) { Toast.warning('Please sign in to book.'); navigate('login'); return; }
      openBookingModal();
    });
    const cfb = $('#booking-confirm-btn');
    if (cfb) cfb.addEventListener('click', confirmBooking);

    // Dashboard tabs
    $$('[data-dash-tab]').forEach(b => b.addEventListener('click', () => {
      if (b.dataset.dashTab === 'admin') { navigate('admin'); return; }
      tab(b.dataset.dashTab);
    }));

    // Admin tabs
    $$('[data-admin-tab]').forEach(b => b.addEventListener('click', () => adminTab(b.dataset.adminTab)));
    const avr = $('[data-verify-refresh]');
    if (avr) avr.addEventListener('click', () => { loadAdminVerifications(); loadAdminStats(); });

    // Socket pushes only arrive while the socket is connected, so an admin tab
    // left open could sit on a stale queue and never show a fresh upload.
    // Poll quietly while the Verifications panel is actually on screen.
    setInterval(() => {
      if (document.visibilityState !== 'visible') return;
      if (!Auth.user || Auth.user.role !== 'admin') return;
      const panel = $('[data-admin-panel="verifications"]');
      if (!panel || !panel.classList.contains('active')) return;
      loadAdminVerifications(true);
    }, 20000);
    const abs = $('#admin-booking-status');
    if (abs) abs.addEventListener('change', loadAdminBookings);
    const aus = $('#admin-user-search');
    if (aus) aus.addEventListener('input', (() => { let t; return () => { clearTimeout(t); t = setTimeout(() => { const q = aus.value.trim(); (async () => {
      const body = $('#admin-users-body');
      const res = await API.get('/admin/users?per_page=50&search=' + encodeURIComponent(q));
      const list = API.ensureOk(res).users || [];
      body.innerHTML = list.map(u => `
        <tr>
          <td><strong>${H.esc(u.full_name)}</strong><br><span class="text-muted" style="font-size:.8125rem">${H.esc(u.email)}</span></td>
          <td>${H.esc(u.user_id)}</td>
          <td>${H.esc(u.phone)}</td>
          <td><span class="badge ${u.role === 'admin' ? 'badge-danger' : 'badge-info'}">${H.esc(u.role)}</span></td>
          <td>${H.inr(u.wallet_balance)}</td>
          <td><span class="badge ${u.is_blocked ? 'badge-danger' : 'badge-success'}">${u.is_blocked ? 'Blocked' : 'Active'}</span></td>
          <td>${u.role !== 'admin' ? `<button class="btn btn-sm ${u.is_blocked ? 'btn-outline' : 'btn-danger'}" data-block-u="${u.id}">${u.is_blocked ? 'Unblock' : 'Block'}</button>` : ''}</td>
        </tr>`).join('') || `<tr><td colspan="7"><div class="empty-state"><p>No users found.</p></div></tr></td></tr>`;
      $$('[data-block-u]', body).forEach(b => b.addEventListener('click', async () => {
        const r2 = await API.put(`/admin/users/${b.dataset.blockU}/block`);
        API.ensureOk(r2); Toast.success('User status updated.'); aus.dispatchEvent(new Event('input'));
      }));
      loadAdminStats();
    })(); }, 400); }; })());

    // Vehicle modal
    $$('[data-vehicle-add-btn]').forEach(b => b.addEventListener('click', openVehicleModal));
    const vs = $('#vehicle-save-btn');
    if (vs) vs.addEventListener('click', saveVehicle);
    const vf = $('#vehicle-form');
    if (vf) vf.addEventListener('submit', e => { e.preventDefault(); saveVehicle(); });

    // Facility modal
    const fa = $('[data-admin-facility-add]');
    if (fa) fa.addEventListener('click', openFacilityModal);
    const fs = $('#facility-save-btn');
    if (fs) fs.addEventListener('click', saveFacility);
    const ff = $('#facility-form');
    if (ff) ff.addEventListener('submit', e => { e.preventDefault(); saveFacility(); });

    // Admin facility view links (delegated)
    document.addEventListener('click', e => {
      const vfLink = e.target.closest('[data-view-fac]');
      if (vfLink) { e.preventDefault(); openFacility(Number(vfLink.dataset.viewFac)); }
    });

    // Modal close
    $$('[data-modal-close]').forEach(b => b.addEventListener('click', () => {
      const backdrop = b.closest('.modal-backdrop');
      if (backdrop) Modal.close(backdrop.id);
    }));
    $$('.modal-backdrop').forEach(b => b.addEventListener('click', e => {
      if (e.target === b) Modal.close(b.id);
    }));
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') Modal.closeAll();
    });

    // Year
    const y = $('[data-year]');
    if (y) y.textContent = new Date().getFullYear();

    // Notifications
    const nb = $('[data-notif-toggle]');
    if (nb) nb.addEventListener('click', (e) => { e.stopPropagation(); toggleNotifPanel(); });
    const nm2 = $('[data-notif-mark-all]');
    if (nm2) nm2.addEventListener('click', () => Notifications.markAllRead());
    const nc = $('[data-notif-clear]');
    if (nc) nc.addEventListener('click', async () => {
      try { await API.ensureOk(await API.delete('/notifications/read-all')); }
      catch (e) { Toast.error('Could not clear notifications.'); return; }
      resetNotifications();
      Toast.success('Notifications cleared.');
    });
    document.addEventListener('click', (e) => {
      if (!e.target.closest('[data-notif]')) toggleNotifPanel(false);
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') toggleNotifPanel(false);
    });

    // Auth restore
    window.AuthChanged(Auth.user);
  }

  /* ============================================================
     BOOT
  ============================================================ */
  function boot() {
    bindGlobal();
    bindAuth();
    refreshNavbar();
    navigate(Auth.isLoggedIn() ? 'home' : 'home');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  window.Parkease = { showToast: (m, t) => Toast.show(m, t) };
})();