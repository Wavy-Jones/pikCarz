/* ============================================
   pikCarz API Integration
   Connects frontend to backend API
   ============================================ */

// API Configuration
const API_CONFIG = {
  BASE_URL: 'https://pikcarz.vercel.app',
  TIMEOUT: 10000
};

// API Helper Functions
const api = {
  // Generic fetch wrapper with error handling
  async request(endpoint, options = {}) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    const token = localStorage.getItem('auth_token');
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
      },
      ...options
    };
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        // Handle expired / invalid session — redirect to sign-in cleanly
        if (response.status === 401) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_data');
          // Only redirect if we're on a protected page (not already on sign-in/register)
          const onAuthPage = window.location.pathname.includes('signin') ||
                             window.location.pathname.includes('register') ||
                             window.location.pathname.includes('forgot-password') ||
                             window.location.pathname.includes('reset-password');
          if (!onAuthPage) {
            window.location.href = 'signin.html?session=expired';
          }
          throw new Error('Your session has expired. Please sign in again.');
        }
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },
  
  // GET request
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  },
  
  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  // PUT request
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },
  
  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};

// Vehicle API
const vehicleAPI = {
  // Get all vehicles with filters
  async getVehicles(filters = {}) {
    const params = {
      page: filters.page || 1,
      per_page: filters.per_page || 20,
      status: 'active', // Only show active vehicles
      ...(filters.category && { category: filters.category }),
      ...(filters.make && { make: filters.make }),
      ...(filters.min_price && { min_price: filters.min_price }),
      ...(filters.max_price && { max_price: filters.max_price }),
      ...(filters.province && { province: filters.province })
    };
    
    return api.get('/api/vehicles', params);
  },
  
  // Get single vehicle by ID
  async getVehicle(id) {
    return api.get(`/api/vehicles/${id}`);
  },
  
  // Create new vehicle listing (requires auth)
  async createVehicle(vehicleData) {
    return api.post('/api/vehicles', vehicleData);
  },

  async uploadVehicleImages(vehicleId, files) {
  const formData = new FormData();
  
  for (let file of files) {
    formData.append('images', file);
  }

  const token = localStorage.getItem('auth_token');

  const response = await fetch(`${API_CONFIG.BASE_URL}/api/vehicles/${vehicleId}/images`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  if (!response.ok) throw new Error('Image upload failed');

  return response.json();
},
  
  // Update vehicle (requires auth)
  async updateVehicle(id, vehicleData) {
    return api.put(`/api/vehicles/${id}`, vehicleData);
  },
  
  // Delete vehicle (requires auth)
  async deleteVehicle(id) {
    return api.delete(`/api/vehicles/${id}`);
  },
  
  // Get user's own listings (requires auth)
  async getMyVehicles(page = 1) {
    return api.get('/api/vehicles/my/listings', { page, per_page: 20 });
  }
};

// Auth API
const authAPI = {
  // Register new user
  async register(userData) {
    const response = await api.post('/api/auth/register', userData);
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
    }
    return response;
  },
  
  // Login user
  async login(email, password) {
    const response = await api.post('/api/auth/login', { email, password });
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
    }
    return response;
  },
  
  // Get current user info
  async getCurrentUser() {
    return api.get('/api/auth/me');
  },
  
  // Logout
  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    window.location.href = 'index.html';
  },
  
  // Check if user is logged in
  isAuthenticated() {
    return !!localStorage.getItem('auth_token');
  },
  
  // Get stored user data
  getUser() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { api, vehicleAPI, authAPI };
}
