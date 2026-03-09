/**
 * Browse Vehicles - Live API Integration
 */

let currentPage = 1;
let currentFilters = {};

// Load vehicles from API
async function loadVehicles(page = 1, filters = {}) {
    const vehiclesGrid = document.getElementById('vehicles-grid');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    // Show loading
    if (loadingSpinner) loadingSpinner.style.display = 'block';
    if (vehiclesGrid) vehiclesGrid.innerHTML = '';

    try {
        const params = { page, per_page: 20, ...filters };
        const response = await api.getVehicles(params);
        
        if (vehiclesGrid) {
            if (response.vehicles && response.vehicles.length > 0) {
                vehiclesGrid.innerHTML = response.vehicles.map(vehicle => createVehicleCard(vehicle)).join('');
            } else {
                vehiclesGrid.innerHTML = '<p class="no-results">No vehicles found. Try adjusting your filters.</p>';
            }
        }

        // Update pagination
        updatePagination(response.page, Math.ceil(response.total / response.per_page));
        
    } catch (error) {
        console.error('Error loading vehicles:', error);
        if (vehiclesGrid) {
            vehiclesGrid.innerHTML = '<p class="error">Failed to load vehicles. Please try again.</p>';
        }
    } finally {
        if (loadingSpinner) loadingSpinner.style.display = 'none';
    }
}

// Create vehicle card HTML
function createVehicleCard(vehicle) {
    const image = vehicle.images && vehicle.images.length > 0 
        ? vehicle.images[0] 
        : 'https://via.placeholder.com/400x300?text=No+Image';
    
    const verifiedBadge = vehicle.is_verified 
        ? '<span class="verified-badge">✓ Verified Dealer</span>' 
        : '';
    
    return `
        <div class="vehicle-card" onclick="viewVehicle(${vehicle.id})">
            <div class="vehicle-image" style="background-image: url('${image}')">
                ${vehicle.status === 'featured' ? '<span class="featured-badge">Featured</span>' : ''}
            </div>
            <div class="vehicle-info">
                <h3 class="vehicle-title">${vehicle.title}</h3>
                <p class="vehicle-price">R ${vehicle.price.toLocaleString()}</p>
                <div class="vehicle-details">
                    <span>${vehicle.year}</span> • 
                    <span>${vehicle.mileage.toLocaleString()} km</span> • 
                    <span>${vehicle.transmission}</span>
                </div>
                <p class="vehicle-location">${vehicle.city}, ${vehicle.province}</p>
                <div class="seller-info">
                    ${verifiedBadge}
                    <span class="seller-name">${vehicle.seller_name}</span>
                </div>
            </div>
        </div>
    `;
}

// View vehicle details
function viewVehicle(id) {
    window.location.href = `vehicle-detail.html?id=${id}`;
}

// Update pagination
function updatePagination(current, total) {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;

    let html = '';
    
    // Previous button
    if (current > 1) {
        html += `<button onclick="loadVehicles(${current - 1}, currentFilters)" class="btn-pagination">Previous</button>`;
    }
    
    // Page numbers
    html += `<span class="page-info">Page ${current} of ${total}</span>`;
    
    // Next button
    if (current < total) {
        html += `<button onclick="loadVehicles(${current + 1}, currentFilters)" class="btn-pagination">Next</button>`;
    }
    
    pagination.innerHTML = html;
}

// Apply filters
function applyFilters() {
    const filters = {
        category: document.getElementById('filter-category')?.value || '',
        make: document.getElementById('filter-make')?.value || '',
        min_price: document.getElementById('filter-min-price')?.value || '',
        max_price: document.getElementById('filter-max-price')?.value || '',
        province: document.getElementById('filter-province')?.value || ''
    };

    // Remove empty filters
    Object.keys(filters).forEach(key => {
        if (!filters[key]) delete filters[key];
    });

    currentFilters = filters;
    loadVehicles(1, filters);
}

// Reset filters
function resetFilters() {
    const form = document.getElementById('filters-form');
    if (form) form.reset();
    currentFilters = {};
    loadVehicles(1);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadVehicles();
    
    // Set up filter form
    const filterForm = document.getElementById('filters-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });
    }
});
