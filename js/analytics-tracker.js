/* ============================================================
   pikCarz — Page View Tracker (Option 2 / own analytics)
   Fires once per page load. Non-blocking, silent on errors.
   No IP addresses or PII sent.
   ============================================================ */
(function () {
  const API_BASE = 'https://pikcarz.vercel.app';

  // ── Session ID: unique per browser tab session ──────────────
  // Uses sessionStorage so it resets when the tab is closed,
  // giving us a reasonable proxy for "visits" vs "page views".
  function getSessionId() {
    const key = 'pkz_sid';
    let sid = sessionStorage.getItem(key);
    if (!sid) {
      sid = 'sid_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
      sessionStorage.setItem(key, sid);
    }
    return sid;
  }

  // ── Device type from user agent ─────────────────────────────
  function getDeviceType() {
    const ua = navigator.userAgent.toLowerCase();
    if (/tablet|ipad|playbook|silk/.test(ua)) return 'tablet';
    if (/mobile|android|iphone|ipod|blackberry|opera mini|iemobile/.test(ua)) return 'mobile';
    return 'desktop';
  }

  // ── Classify referrer source ────────────────────────────────
  function cleanReferrer() {
    const ref = document.referrer;
    if (!ref) return null;
    // Strip query params from internal referrers to avoid leaking search terms
    try {
      const url = new URL(ref);
      if (url.hostname.includes('pikcarz.co.za')) return url.pathname;
      return ref.slice(0, 200); // truncate long external referrers
    } catch (_) {
      return ref.slice(0, 200);
    }
  }

  // ── Logged-in user ID (if available) ───────────────────────
  function getUserId() {
    try {
      const ud = localStorage.getItem('user_data');
      return ud ? JSON.parse(ud).id || null : null;
    } catch (_) { return null; }
  }

  // ── Fire the tracking request ────────────────────────────────
  function track() {
    const payload = {
      page_url:    window.location.pathname + window.location.search,
      page_title:  document.title,
      referrer:    cleanReferrer(),
      device_type: getDeviceType(),
      session_id:  getSessionId(),
      user_id:     getUserId(),
    };

    // Use sendBeacon when available (non-blocking, survives page unload)
    const body = JSON.stringify(payload);
    const url  = API_BASE + '/api/analytics/track';

    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, new Blob([body], { type: 'application/json' }));
    } else {
      // Fallback: fire-and-forget fetch
      fetch(url, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    body,
        keepalive: true,
      }).catch(() => {/* silent — analytics must never break the page */});
    }
  }

  // Run after the page has loaded to avoid slowing down render
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', track);
  } else {
    track();
  }
})();
