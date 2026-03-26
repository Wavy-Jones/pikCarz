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
  const user = getCurrentUser();
  
  if (!mobileMenu) return;
  
  if (isLoggedIn() && user) {
    // User is logged in
    const isAdmin = user.role === 'admin';
    const dashboardUrl = isAdmin ? 'admin-dashboard.html' : 'dashboard.html';
    const dashboardText = isAdmin ? 'Admin Dashboard' : 'My Dashboard';
    
    // Find the last link and replace it
    const links = mobileMenu.querySelectorAll('a');
    if (links.length > 0) {
      const lastLink = links[links.length - 1];
      lastLink.href = dashboardUrl;
      lastLink.textContent = dashboardText;
      lastLink.style.color = 'var(--accent)';
      
      // Add logout link
      if (!mobileMenu.querySelector('.mobile-logout')) {
        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'mobile-logout';
        logoutBtn.textContent = 'Logout';
        logoutBtn.onclick = logout;
        logoutBtn.style.cssText = 'width: 100%; padding: 16px 24px; background: none; border: none; color: var(--muted); text-align: left; cursor: pointer; font-size: 1rem;';
        mobileMenu.appendChild(logoutBtn);
      }
    }
  }
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
