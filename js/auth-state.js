/* ============================================
   pikCarz - Global Authentication State Manager
   ============================================
   This file checks auth state and updates UI across all pages
*/

// Check if user is logged in
function isLoggedIn() {
  const token = localStorage.getItem('auth_token');
  const userData = localStorage.getItem('user_data');
  return !!(token && userData);
}

// Get current user data
function getCurrentUser() {
  const userData = localStorage.getItem('user_data');
  return userData ? JSON.parse(userData) : null;
}

// Logout function
function logout() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_data');
  window.location.href = 'index.html';
}

// Update navbar based on auth state
function updateNavbar() {
  const navActions = document.querySelector('.nav-actions');
  const user = getCurrentUser();
  
  if (!navActions) return;
  
  if (isLoggedIn() && user) {
    // User is logged in - show Dashboard + Logout
    const isAdmin = user.role === 'admin';
    const dashboardUrl = isAdmin ? 'admin-dashboard.html' : 'dashboard.html';
    const dashboardText = isAdmin ? 'Admin Dashboard' : 'My Dashboard';
    
    navActions.innerHTML = `
      <a href="${dashboardUrl}" class="btn-ghost">${dashboardText}</a>
      <button onclick="logout()" class="btn-secondary" style="cursor: pointer;">
        <svg width="14" height="14" viewBox="0 0 24 24" stroke="currentColor" fill="none" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        Logout
      </button>
    `;
  } else {
    // User is logged out - show Sign In + Sign Up
    navActions.innerHTML = `
      <a href="signin.html" class="btn-ghost">Sign In</a>
      <a href="register.html" class="btn-secondary">Sign Up</a>
      <a href="signin.html" class="btn-primary">
        <svg width="14" height="14" viewBox="0 0 24 24" stroke="currentColor" fill="none" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        List Vehicle
      </a>
    `;
  }
}

// Update mobile menu based on auth state
function updateMobileMenu() {
  const mobileMenu = document.querySelector('.mobile-menu');
  if (!mobileMenu) return;

  const user = getCurrentUser();
  const closeBtn = mobileMenu.querySelector('.mobile-close');

  if (isLoggedIn() && user) {
    const isAdmin = user.role === 'admin';
    const dashboardUrl = isAdmin ? 'admin-dashboard.html' : 'dashboard.html';
    const dashboardText = isAdmin ? 'Admin Dashboard' : 'My Dashboard';

    mobileMenu.innerHTML = `
      <button class="mobile-close" aria-label="Close menu">
        <svg viewBox="0 0 24 24" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
      <a href="index.html">Home</a>
      <a href="browse.html">Browse Vehicles</a>
      <a href="about.html">About Us</a>
      <a href="contact.html">Contact</a>
      <a href="${dashboardUrl}" style="color:var(--accent)">${dashboardText}</a>
      <button class="mobile-logout" onclick="logout()" style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;font-weight:700;color:var(--muted);background:none;border:none;cursor:pointer;letter-spacing:-0.5px;">Logout</button>
    `;
  } else {
    mobileMenu.innerHTML = `
      <button class="mobile-close" aria-label="Close menu">
        <svg viewBox="0 0 24 24" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
      <a href="index.html">Home</a>
      <a href="browse.html">Browse Vehicles</a>
      <a href="about.html">About Us</a>
      <a href="contact.html">Contact</a>
      <a href="signin.html">Sign In</a>
      <a href="register.html" style="color:var(--accent)">Sign Up</a>
    `;
  }

  // Re-attach close button listener after rebuilding
  mobileMenu.querySelector('.mobile-close')?.addEventListener('click', () => mobileMenu.classList.remove('open'));
  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => mobileMenu.classList.remove('open')));
}

// Protect dashboard pages (redirect if not logged in)
function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = 'signin.html';
    return false;
  }
  return true;
}

// Protect admin pages (redirect if not admin)
function requireAdmin() {
  const user = getCurrentUser();
  if (!isLoggedIn() || !user || user.role !== 'admin') {
    window.location.href = 'index.html';
    return false;
  }
  return true;
}

// Initialize auth state on page load
document.addEventListener('DOMContentLoaded', () => {
  updateNavbar();
  updateMobileMenu();
});

// Make logout function globally available
window.logout = logout;
window.isLoggedIn = isLoggedIn;
window.getCurrentUser = getCurrentUser;
window.requireAuth = requireAuth;
window.requireAdmin = requireAdmin;
