/**
 * pikCarz API Client
 * Connects frontend to live backend API
 */

const API_BASE_URL = 'https://pikcarz.vercel.app';

class PikCarzAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('access_token');
    }

    // Helper: Make authenticated request
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth Methods
    async register(userData) {
        const response = await this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        
        return response;
    }

    async login(email, password) {
        const response = await this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        
        return response;
    }

    async getCurrentUser() {
        return await this.request('/api/auth/me');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
    }

    isAuthenticated() {
        return !!this.token;
    }

    // Vehicle Methods
    async getVehicles(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/api/vehicles?${params}`);
    }

    async getVehicle(id) {
        return await this.request(`/api/vehicles/${id}`);
    }

    async createVehicle(vehicleData) {
        return await this.request('/api/vehicles', {
            method: 'POST',
            body: JSON.stringify(vehicleData)
        });
    }

    async updateVehicle(id, vehicleData) {
        return await this.request(`/api/vehicles/${id}`, {
            method: 'PUT',
            body: JSON.stringify(vehicleData)
        });
    }

    async deleteVehicle(id) {
        return await this.request(`/api/vehicles/${id}`, {
            method: 'DELETE'
        });
    }

    async getMyVehicles(page = 1) {
        return await this.request(`/api/vehicles/my/listings?page=${page}`);
    }

    async uploadVehicleImages(vehicleId, files) {
        const formData = new FormData();
        
        for (let file of files) {
            formData.append('files', file);
        }

        const response = await fetch(`${this.baseURL}/api/vehicles/${vehicleId}/images`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Image upload failed');
        }

        return await response.json();
    }

    // Subscription Methods
    async getSubscriptionPlans() {
        return await this.request('/api/subscriptions/plans');
    }

    async subscribe(tier) {
        return await this.request('/api/subscriptions/subscribe', {
            method: 'POST',
            body: JSON.stringify({ subscription_tier: tier })
        });
    }

    async getMySubscription() {
        return await this.request('/api/subscriptions/my/subscription');
    }

    async getMyPayments() {
        return await this.request('/api/subscriptions/my/payments');
    }

    // Admin Methods (require admin auth)
    async getPendingVehicles(page = 1) {
        return await this.request(`/api/admin/vehicles/pending?page=${page}`);
    }

    async approveVehicle(id) {
        return await this.request(`/api/admin/vehicles/${id}/approve`, {
            method: 'PUT'
        });
    }

    async rejectVehicle(id) {
        return await this.request(`/api/admin/vehicles/${id}/reject`, {
            method: 'PUT'
        });
    }

    async getAdminStats() {
        return await this.request('/api/admin/stats');
    }
}

// Create global API instance
const api = new PikCarzAPI();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PikCarzAPI;
}
