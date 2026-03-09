/**
 * Authentication Modal & User Management
 */

// Show login modal
function showLoginModal() {
    const modal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form-container');
    const registerForm = document.getElementById('register-form-container');
    
    if (modal) {
        modal.style.display = 'flex';
        if (loginForm) loginForm.style.display = 'block';
        if (registerForm) registerForm.style.display = 'none';
    }
}

// Show register modal
function showRegisterModal() {
    const modal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form-container');
    const registerForm = document.getElementById('register-form-container');
    
    if (modal) {
        modal.style.display = 'flex';
        if (loginForm) loginForm.style.display = 'none';
        if (registerForm) registerForm.style.display = 'block';
    }
}

// Close modal
function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) modal.style.display = 'none';
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';
        
        const response = await api.login(email, password);
        
        if (response.access_token) {
            closeAuthModal();
            updateUIForLoggedInUser(response.user);
            showNotification('Login successful!', 'success');
            
            // Redirect to dashboard if on homepage
            if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
                window.location.href = 'dashboard.html';
            }
        }
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.message || 'Login failed. Please check your credentials.';
            errorDiv.style.display = 'block';
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
}

// Handle registration
async function handleRegister(event) {
    event.preventDefault();
    
    const userData = {
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        full_name: document.getElementById('register-name').value,
        phone: document.getElementById('register-phone')?.value || null,
        role: document.getElementById('register-role')?.value || 'individual'
    };
    
    const errorDiv = document.getElementById('register-error');
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';
        
        const response = await api.register(userData);
        
        if (response.access_token) {
            closeAuthModal();
            updateUIForLoggedInUser(response.user);
            showNotification('Account created successfully!', 'success');
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.message || 'Registration failed. Please try again.';
            errorDiv.style.display = 'block';
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
    }
}

// Update UI for logged in user
function updateUIForLoggedInUser(user) {
    // Update nav buttons
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    
    if (authButtons) authButtons.style.display = 'none';
    if (userMenu) {
        userMenu.style.display = 'block';
        const userName = userMenu.querySelector('.user-name');
        if (userName) userName.textContent = user.full_name || user.email;
    }
}

// Logout
function logout() {
    api.logout();
    window.location.href = 'index.html';
}

// Check authentication on page load
async function checkAuth() {
    if (api.isAuthenticated()) {
        try {
            const user = await api.getCurrentUser();
            updateUIForLoggedInUser(user);
        } catch (error) {
            // Token might be expired
            api.logout();
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', checkAuth);

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('auth-modal');
    if (event.target === modal) {
        closeAuthModal();
    }
});
