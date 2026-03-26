/**
 * Dashboard - Manage Listings & Subscription
 */

let currentUser = null;
let currentSubscription = null;

// Initialize dashboard
async function initDashboard() {
    // Check authentication
    if (!authAPI.isAuthenticated()) {
        window.location.href = 'signin.html';
        return;
    }

    try {
        // Load user data
        currentUser = await authAPI.getCurrentUser();
        
        // Load subscription info
        await loadSubscriptionInfo();
        
        // Load user listings
        await loadMyListings();
        
    } catch (error) {
        console.error('Dashboard init error:', error);
        showNotification('Failed to load dashboard data', 'error');
    }
}

// Load subscription info
async function loadSubscriptionInfo() {
    try {
        currentSubscription = await api.getMySubscription();
        
        const tierElement = document.querySelector('.subscription-tier');
        const expiresElement = document.querySelector('.subscription-expires');
        
        if (tierElement) {
            tierElement.textContent = `${currentSubscription.current_plan.name} Plan - R${currentSubscription.current_plan.price}/month`;
        }
        
        if (expiresElement && currentSubscription.expires_at) {
            const expiryDate = new Date(currentSubscription.expires_at);
            expiresElement.textContent = `Expires: ${expiryDate.toLocaleDateString()}`;
        }
    } catch (error) {
        console.error('Error loading subscription:', error);
        const tierElement = document.querySelector('.subscription-tier');
        const expiresElement = document.querySelector('.subscription-expires');
        if (tierElement) tierElement.textContent = 'No Active Plan';
        if (expiresElement) expiresElement.textContent = 'Subscribe to list your vehicles';
    }
}

// Load user's listings
async function loadMyListings() {
    const grid = document.getElementById('my-listings-grid');
    
    try {
        const response = await vehicleAPI.getMyVehicles();
        
        if (response.vehicles && response.vehicles.length > 0) {
            grid.innerHTML = response.vehicles.map(vehicle => createMyListingCard(vehicle)).join('');
            
            // Update stats
            updateStats(response.vehicles);
        } else {
            grid.innerHTML = '<p class="no-listings">You haven\'t created any listings yet. <a href="#" onclick="showCreateListingModal()">Create your first listing</a></p>';
        }
    } catch (error) {
        console.error('Error loading listings:', error);
        grid.innerHTML = '<p class="error">Failed to load listings</p>';
    }
}

// Create listing card for dashboard
function createMyListingCard(vehicle) {
    const image = vehicle.images && vehicle.images.length > 0 
        ? vehicle.images[0] 
        : 'https://via.placeholder.com/300x200?text=No+Image';
    
    const statusClass = vehicle.status === 'active' ? 'status-active' : 
                       vehicle.status === 'pending' ? 'status-pending' : 'status-inactive';
    
    return `
        <div class="my-listing-card">
            <div class="listing-image" style="background-image: url('${image}')"></div>
            <div class="listing-details">
                <h3>${vehicle.title}</h3>
                <p class="listing-price">R ${vehicle.price.toLocaleString()}</p>
                <p class="listing-status ${statusClass}">${vehicle.status.toUpperCase()}</p>
                <div class="listing-actions">
                    <button onclick="editListing(${vehicle.id})" class="btn-secondary">Edit</button>
                    <button onclick="deleteListing(${vehicle.id})" class="btn-danger">Delete</button>
                </div>
            </div>
        </div>
    `;
}

// Update stats
function updateStats(vehicles) {
    const activeCount = vehicles.filter(v => v.status === 'active').length;
    const pendingCount = vehicles.filter(v => v.status === 'pending').length;
    
    document.getElementById('stat-active').textContent = activeCount;
    document.getElementById('stat-pending').textContent = pendingCount;
    // Views would come from analytics (not implemented yet)
}

// Show create listing modal
function showCreateListingModal() {
    const modal = document.getElementById('create-listing-modal');
    if (modal) modal.style.display = 'flex';
}

// Close create listing modal
function closeCreateListingModal() {
    const modal = document.getElementById('create-listing-modal');
    if (modal) modal.style.display = 'none';
    document.getElementById('create-listing-form').reset();
}

// Handle create listing
async function handleCreateListing(event) {
    event.preventDefault();
    
    const vehicleData = {
        make: document.getElementById('vehicle-make').value,
        model: document.getElementById('vehicle-model').value,
        year: parseInt(document.getElementById('vehicle-year').value),
        category: document.getElementById('vehicle-category').value,
        price: parseFloat(document.getElementById('vehicle-price').value),
        mileage: parseInt(document.getElementById('vehicle-mileage').value),
        transmission: document.getElementById('vehicle-transmission').value,
        fuel_type: document.getElementById('vehicle-fuel').value,
        color: document.getElementById('vehicle-color').value,
        province: document.getElementById('vehicle-province').value,
        city: document.getElementById('vehicle-city').value,
        title: document.getElementById('vehicle-title').value,
        description: document.getElementById('vehicle-description').value
    };
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const errorDiv = document.getElementById('create-listing-error');
    
    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';
        
        // Create vehicle
        const vehicle = await vehicleAPI.createVehicle(vehicleData);
        
        // Upload images if selected
        const imageInput = document.getElementById('vehicle-images');
        if (imageInput.files.length > 0) {
            await vehicleAPI.uploadVehicleImages(vehicle.id, imageInput.files);
        }
        
        closeCreateListingModal();
        showNotification('Listing created successfully! Pending admin approval.', 'success');
        loadMyListings();
        
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.message || 'Failed to create listing';
            errorDiv.style.display = 'block';
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Listing';
    }
}

// Delete listing
async function deleteListing(id) {
    if (!confirm('Are you sure you want to delete this listing?')) {
        return;
    }
    
    try {
        await vehicleAPI.deleteVehicle(id);
        showNotification('Listing deleted successfully', 'success');
        loadMyListings();
    } catch (error) {
        showNotification('Failed to delete listing', 'error');
    }
}

// Show subscription plans
async function showSubscriptionPlans() {
    const modal = document.getElementById('subscription-modal');
    const grid = document.getElementById('subscription-plans-grid');
    
    try {
        const plans = await subscriptionAPI.getPlans();
        
        grid.innerHTML = plans.map(plan => `
            <div class="plan-card">
                <h3>${plan.name}</h3>
                <p class="plan-price">R ${plan.price}/month</p>
                <ul class="plan-features">
                    ${plan.features.map(f => `<li>${f}</li>`).join('')}
                </ul>
                <button onclick="subscribeToPlan('${plan.tier}')" class="btn-primary">
                    ${currentSubscription && currentSubscription.current_plan.tier === plan.tier ? 'Current Plan' : 'Upgrade'}
                </button>
            </div>
        `).join('');
        
        modal.style.display = 'flex';
        
    } catch (error) {
        showNotification('Failed to load subscription plans', 'error');
    }
}

// Subscribe to plan
async function subscribeToPlan(tier) {
    try {
        const response = await subscriptionAPI.subscribe(tier);
        
        if (response.payment_url) {
            // Redirect to PayFast
            window.location.href = response.payment_url;
        }
    } catch (error) {
        showNotification('Failed to initiate subscription', 'error');
    }
}

// Close subscription modal
function closeSubscriptionModal() {
    const modal = document.getElementById('subscription-modal');
    if (modal) modal.style.display = 'none';
}

// Edit listing (redirect to edit page or open modal)
function editListing(id) {
    // For now, just show notification
    // In production, you'd open an edit modal or redirect to edit page
    showNotification('Edit functionality coming soon!', 'info');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initDashboard);
