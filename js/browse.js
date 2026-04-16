/* ============================================
   pikCarz Browse Page - Real API Integration
   ============================================ */

// ── Global toggle — must be at top level so onclick attributes can reach it ──
window.toggleSave = function(btn) {
  btn.classList.toggle('saved');
  const svg = btn.querySelector('svg');
  if (btn.classList.contains('saved')) {
    svg.style.fill   = '#F05A1A';
    svg.style.stroke = '#F05A1A';
    btn.setAttribute('aria-label', 'Unsave');
  } else {
    svg.style.fill   = 'none';
    svg.style.stroke = 'currentColor';
    btn.setAttribute('aria-label', 'Save');
  }
};

document.addEventListener('DOMContentLoaded', async () => {
  
  // Current filters
  let currentFilters = {
    page: 1,
    per_page: 20,
    category: '',
    make: '',
    min_price: '',
    max_price: '',
    province: ''
  };
  
  // Read URL parameters on page load
  const urlParams = new URLSearchParams(window.location.search);
  const urlType = urlParams.get('type');
  
  if (urlType) {
    const typeMap = {
      'all': '',
      'new-cars': 'new_car',
      'used-cars': 'used_car',
      'motorbikes': 'motorcycle',
      'trucks': 'truck',
      'other': 'other'
    };
    currentFilters.category = typeMap[urlType] || '';
    
    document.querySelectorAll('.cat-chip').forEach(chip => {
      const chipText = chip.textContent.trim().toLowerCase();
      const chipMap = {
        'all vehicles': 'all',
        'new cars': 'new-cars',
        'used cars': 'used-cars',
        'motorbikes': 'motorbikes',
        'trucks & bakkies': 'trucks',
        'other vehicles': 'other'
      };
      if (chipMap[chipText] === urlType) {
        chip.classList.add('active');
      } else {
        chip.classList.remove('active');
      }
    });
  }
  
  await loadVehicles();
  
  document.querySelector('.filter-btn')?.addEventListener('click', async () => {
    currentFilters.page = 1;
    await loadVehicles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  
  document.querySelector('.sort-select')?.addEventListener('change', async () => {
    await loadVehicles();
  });
  
  document.querySelectorAll('.cat-chip').forEach(chip => {
    chip.addEventListener('click', async (e) => {
      document.querySelectorAll('.cat-chip').forEach(c => c.classList.remove('active'));
      e.currentTarget.classList.add('active');
      const category = e.currentTarget.textContent.trim().toLowerCase();
      const categoryMap = {
        'all vehicles': '',
        'new cars': 'new_car',
        'used cars': 'used_car',
        'motorbikes': 'motorcycle',
        'trucks & bakkies': 'truck',
        'other': 'other'
      };
      currentFilters.category = categoryMap[category] || '';
      currentFilters.page = 1;
      await loadVehicles();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
  
  document.querySelector('.btn-primary')?.addEventListener('click', async (e) => {
    if (e.target.textContent.includes('Load More')) {
      currentFilters.page++;
      await loadVehicles(true);
    }
  });
  
  async function loadVehicles(append = false) {
    const gridContainer = document.querySelector('.vehicles-grid');
    const resultsCount  = document.querySelector('.results-count');
    
    if (!gridContainer) return;
    
    if (!append) {
      gridContainer.innerHTML = '<p style="grid-column: 1/-1; text-align:center; padding:60px; color:var(--muted)">Loading vehicles...</p>';
    }
    
    try {
      updateFiltersFromForm();
      
      const data = await vehicleAPI.getVehicles(currentFilters);
      
      if (resultsCount) {
        const showing = append
          ? gridContainer.querySelectorAll('.vehicle-card').length + data.vehicles.length
          : data.vehicles.length;
        resultsCount.innerHTML = `Showing <strong>${showing}</strong> of <strong>${data.total}</strong> vehicles`;
        if (!append) {
          resultsCount.style.transition = 'background 0.3s';
          resultsCount.style.background = 'rgba(240,90,26,0.12)';
          resultsCount.style.borderRadius = '6px';
          resultsCount.style.padding = '6px 10px';
          setTimeout(() => { resultsCount.style.background = 'transparent'; }, 1200);
        }
      }
      
      if (data.vehicles.length === 0 && !append) {
        gridContainer.innerHTML = `
          <div style="grid-column: 1/-1; text-align:center; padding:80px 20px;">
            <svg viewBox="0 0 24 24" width="64" height="64" stroke="var(--muted)" fill="none" stroke-width="2" style="margin:0 auto 24px">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <h3 style="color:var(--white); margin-bottom:12px;">No Vehicles Found</h3>
            <p style="color:var(--muted)">Try adjusting your filters or browse all vehicles.</p>
            <button onclick="window.location.reload()" class="btn-primary" style="margin-top:24px">Clear Filters</button>
          </div>
        `;
        return;
      }
      
      const vehiclesHTML = data.vehicles.map(createVehicleCard).join('');
      
      if (append) {
        gridContainer.insertAdjacentHTML('beforeend', vehiclesHTML);
      } else {
        gridContainer.innerHTML = vehiclesHTML;
      }
      
      const loadMoreBtn = document.querySelector('.btn-primary');
      if (loadMoreBtn && loadMoreBtn.textContent.includes('Load More')) {
        const totalLoaded = gridContainer.querySelectorAll('.vehicle-card').length;
        loadMoreBtn.style.display = totalLoaded >= data.total ? 'none' : 'block';
      }
      
    } catch (error) {
      console.error('Error loading vehicles:', error);
      gridContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align:center; padding:60px; color:#ef4444;">
          <h3>Error Loading Vehicles</h3>
          <p>${error.message}</p>
          <button onclick="window.location.reload()" class="btn-primary" style="margin-top:20px">Retry</button>
        </div>
      `;
    }
  }
  
  function updateFiltersFromForm() {
    const typeSelect = document.querySelector('.filter-group select');
    if (typeSelect?.value) {
      const categoryMap = {
        'New Car': 'new_car',
        'Used Car': 'used_car',
        'Motorbike': 'motorcycle',
        'Truck / Bakkie': 'truck',
        'Other': 'other'
      };
      currentFilters.category = categoryMap[typeSelect.value] || '';
    }
    
    const makeInputs = document.querySelectorAll('.filter-group select');
    if (makeInputs[1]?.value) {
      currentFilters.make = makeInputs[1].value;
    }
    
    const priceSelect = document.querySelectorAll('.filter-group select')[3];
    if (priceSelect?.value) {
      if (priceSelect.value === '900000+') {
        currentFilters.min_price = 900000;
        currentFilters.max_price = '';
      } else {
        const [min, max] = priceSelect.value.split('-');
        currentFilters.min_price = min || '';
        currentFilters.max_price = max || '';
      }
    } else {
      currentFilters.min_price = '';
      currentFilters.max_price = '';
    }
    
    const provinceSelect = document.querySelector('.filter-group select:last-of-type');
    if (provinceSelect?.value) {
      currentFilters.province = provinceSelect.value;
    }
  }
  
  function createVehicleCard(vehicle) {
    const badgeClass = vehicle.category === 'new_car'    ? 'badge-new'  :
                       vehicle.category === 'used_car'   ? 'badge-used' :
                       vehicle.category === 'motorcycle' ? 'badge-bike' : 'badge-truck';
    const badgeText  = vehicle.category === 'new_car'    ? 'New'       :
                       vehicle.category === 'used_car'   ? 'Used'      :
                       vehicle.category === 'motorcycle' ? 'Motorbike' : 'Truck';
    
    const imageUrl = vehicle.images && vehicle.images.length > 0
      ? vehicle.images[0]
      : 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=600&q=80';
    
    const verifiedBadge = vehicle.is_verified
      ? '<span class="card-badge badge-featured" style="left:auto;right:12px;top:50px;">Verified</span>'
      : '';

    // Use contact_name for admin on-behalf listings, else seller_name
    const sellerName = vehicle.contact_name || vehicle.seller_name || 'Seller';
    const initials   = sellerName.substring(0, 2).toUpperCase();

    return `
      <article class="vehicle-card" onclick="window.location='vehicle-detail.html?id=${vehicle.id}'">
        <div class="card-img">
          <img src="${imageUrl}" alt="${vehicle.year} ${vehicle.make} ${vehicle.model}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1555215695-3004980ad54e?w=600&q=80'"/>
          <span class="card-badge ${badgeClass}">${badgeText}</span>
          ${verifiedBadge}
          <button class="card-save" onclick="event.stopPropagation(); toggleSave(this)" aria-label="Save">
            <svg viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </button>
        </div>
        <div class="card-body">
          <div class="card-make">${vehicle.make}</div>
          <div class="card-title">${vehicle.model}</div>
          <div class="card-price">R ${Number(vehicle.price).toLocaleString('en-ZA')}</div>
          <div class="card-specs">
            <span class="spec-tag">${vehicle.year}</span>
            <span class="spec-tag">${(vehicle.mileage || 0).toLocaleString()} km</span>
            ${vehicle.transmission ? `<span class="spec-tag">${vehicle.transmission}</span>` : ''}
            ${vehicle.fuel_type    ? `<span class="spec-tag">${vehicle.fuel_type}</span>`    : ''}
          </div>
        </div>
        <div class="card-footer">
          <div class="card-seller">
            <div class="seller-av">${initials}</div>
            <span class="seller-name">${sellerName}</span>
          </div>
          <div class="card-loc">
            <svg viewBox="0 0 24 24" stroke="currentColor" fill="none" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            ${vehicle.city || vehicle.province}
          </div>
        </div>
      </article>
    `;
  }
  
});
