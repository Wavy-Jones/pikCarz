/* ============================================
   pikCarz Browse Page — js/browse.js
   DB enum values: new_car | used_car | motorbike | truck | other
   ============================================ */

// ── Favourite toggle ──────────────────────────────────────────────────────────
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

// ── Category label map ────────────────────────────────────────────────────────
const CATEGORY_LABELS = {
  new_car:   'New Car',
  used_car:  'Used Car',
  motorbike: 'Motorbike',
  truck:     'Trucks & Bakkies',
  other:     'Other',
};

// ── Filter panel toggle ───────────────────────────────────────────────────────
window.toggleFilterPanel = function() {
  const panel = document.getElementById('filter-panel');
  const btn   = document.getElementById('filter-toggle-btn');
  const open  = panel.classList.toggle('open');
  btn.classList.toggle('active', open);
};

// ── Clear all filters ─────────────────────────────────────────────────────────
window.clearAllFilters = function() {
  ['f-category','f-make','f-model','f-year-from','f-price','f-province','f-transmission','f-fuel']
    .forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
  const searchInput = document.getElementById('browse-search-input');
  if (searchInput) searchInput.value = '';
  currentFilters = {
    page: 1, per_page: 20,
    category: '', make: '', model: '', keyword: '',
    min_price: '', max_price: '', province: '',
    transmission: '', fuel_type: ''
  };
  updateActiveFilterTags();
  loadVehicles();
};

// ── Current filters state ─────────────────────────────────────────────────────
let currentFilters = {
  page:         1,
  per_page:     20,
  category:     '',
  make:         '',
  model:        '',
  keyword:      '',
  min_price:    '',
  max_price:    '',
  province:     '',
  transmission: '',
  fuel_type:    '',
};

// ── Active filter tag display ─────────────────────────────────────────────────
function updateActiveFilterTags() {
  const container = document.getElementById('active-filter-tags');
  if (!container) return;

  const tags = [];
  if (currentFilters.category) {
    tags.push({ label: CATEGORY_LABELS[currentFilters.category] || currentFilters.category, key: 'category' });
  }
  if (currentFilters.make)         tags.push({ label: currentFilters.make, key: 'make' });
  if (currentFilters.province)     tags.push({ label: currentFilters.province, key: 'province' });
  if (currentFilters.transmission) tags.push({ label: currentFilters.transmission, key: 'transmission' });
  if (currentFilters.fuel_type)    tags.push({ label: currentFilters.fuel_type, key: 'fuel_type' });
  if (currentFilters.keyword)      tags.push({ label: `"${currentFilters.keyword}"`, key: 'keyword' });
  if (currentFilters.min_price || currentFilters.max_price) {
    const lo = currentFilters.min_price ? `R${Number(currentFilters.min_price).toLocaleString('en-ZA')}` : 'R0';
    const hi = currentFilters.max_price ? `R${Number(currentFilters.max_price).toLocaleString('en-ZA')}` : '+';
    tags.push({ label: `${lo} – ${hi}`, key: 'price' });
  }

  container.innerHTML = tags.map(t => `
    <span class="active-filter-tag">
      ${t.label}
      <button onclick="removeFilterTag('${t.key}')" title="Remove filter">&times;</button>
    </span>`).join('');
}

window.removeFilterTag = function(key) {
  if (key === 'category') { currentFilters.category = ''; const el = document.getElementById('f-category'); if (el) el.value = ''; }
  if (key === 'make')     { currentFilters.make = '';     const el = document.getElementById('f-make');     if (el) el.value = ''; }
  if (key === 'province') { currentFilters.province = ''; const el = document.getElementById('f-province'); if (el) el.value = ''; }
  if (key === 'transmission') { currentFilters.transmission = ''; const el = document.getElementById('f-transmission'); if (el) el.value = ''; }
  if (key === 'fuel_type')    { currentFilters.fuel_type = '';    const el = document.getElementById('f-fuel');          if (el) el.value = ''; }
  if (key === 'keyword')      { currentFilters.keyword = '';      const si = document.getElementById('browse-search-input'); if (si) si.value = ''; }
  if (key === 'price') { currentFilters.min_price = ''; currentFilters.max_price = ''; const el = document.getElementById('f-price'); if (el) el.value = ''; }
  currentFilters.page = 1;
  updateActiveFilterTags();
  loadVehicles();
};

// ── DOMContentLoaded ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {

  // ── Read URL params ──────────────────────────────────────────────────────────
  const urlParams = new URLSearchParams(window.location.search);

  // ?type= — direct DB enum value (new_car, used_car, motorbike, truck, other)
  // 'bakkie' is accepted as a friendly alias for 'truck'
  const rawType = urlParams.get('type') || '';
  const urlType = rawType === 'bakkie' ? 'truck' : rawType;
  if (urlType && ['new_car','used_car','motorbike','truck','other'].includes(urlType)) {
    currentFilters.category = urlType;
    const catSelect = document.getElementById('f-category');
    if (catSelect) catSelect.value = urlType;
  }

  // ?kw= — keyword search from homepage
  const urlKw = urlParams.get('kw') || '';
  if (urlKw) {
    currentFilters.keyword = urlKw;
    const si = document.getElementById('browse-search-input');
    if (si) si.value = urlKw;
  }

  // If URL had any params, open the filter panel so user sees what's active
  if (urlType) {
    const panel = document.getElementById('filter-panel');
    const btn   = document.getElementById('filter-toggle-btn');
    if (panel) panel.classList.add('open');
    if (btn)   btn.classList.add('active');
  }

  updateActiveFilterTags();
  await loadVehicles();

  // ── Apply filters button ─────────────────────────────────────────────────────
  document.getElementById('apply-filters-btn')?.addEventListener('click', async () => {
    readFiltersFromForm();
    currentFilters.page = 1;
    updateActiveFilterTags();
    await loadVehicles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // ── Search button ────────────────────────────────────────────────────────────
  document.getElementById('browse-search-btn')?.addEventListener('click', async () => {
    readFiltersFromForm();
    currentFilters.page = 1;
    updateActiveFilterTags();
    await loadVehicles();
  });

  document.getElementById('browse-search-input')?.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      readFiltersFromForm();
      currentFilters.page = 1;
      updateActiveFilterTags();
      await loadVehicles();
    }
  });

  // ── Sort dropdown ────────────────────────────────────────────────────────────
  document.getElementById('sort-select')?.addEventListener('change', async () => {
    currentFilters.page = 1;
    await loadVehicles();
  });

  // ── Load More ────────────────────────────────────────────────────────────────
  document.querySelector('.load-more-btn')?.addEventListener('click', async () => {
    currentFilters.page++;
    await loadVehicles(true);
  });

});

// ── Read form values into currentFilters ──────────────────────────────────────
function readFiltersFromForm() {
  const cat = document.getElementById('f-category')?.value || '';
  currentFilters.category = cat;

  currentFilters.make     = document.getElementById('f-make')?.value     || '';
  currentFilters.province = document.getElementById('f-province')?.value || '';
  currentFilters.transmission = document.getElementById('f-transmission')?.value || '';
  currentFilters.fuel_type    = document.getElementById('f-fuel')?.value          || '';

  // Search keyword
  const kw = document.getElementById('browse-search-input')?.value.trim() || '';
  currentFilters.keyword = kw;

  // Price
  const priceVal = document.getElementById('f-price')?.value || '';
  if (priceVal === '900000+') {
    currentFilters.min_price = 900000;
    currentFilters.max_price = '';
  } else if (priceVal) {
    const [min, max] = priceVal.split('-');
    currentFilters.min_price = min || '';
    currentFilters.max_price = max || '';
  } else {
    currentFilters.min_price = '';
    currentFilters.max_price = '';
  }
}

// ── Main load function ────────────────────────────────────────────────────────
async function loadVehicles(append = false) {
  const grid     = document.getElementById('vehicles-grid');
  const countEl  = document.getElementById('results-count');
  const loadMore = document.querySelector('.load-more-btn');
  if (!grid) return;

  if (!append) {
    grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:60px;color:var(--muted)">Loading vehicles…</p>';
    if (loadMore) loadMore.style.display = 'none';
  }

  try {
    const sort = document.getElementById('sort-select')?.value || '';
    const params = {
      page:     currentFilters.page,
      per_page: currentFilters.per_page,
      status:   'active',
    };
    if (currentFilters.category)     params.category     = currentFilters.category;
    if (currentFilters.make)         params.make         = currentFilters.make;
    if (currentFilters.min_price)    params.min_price    = currentFilters.min_price;
    if (currentFilters.max_price)    params.max_price    = currentFilters.max_price;
    if (currentFilters.province)     params.province     = currentFilters.province;
    if (currentFilters.transmission) params.transmission = currentFilters.transmission;
    if (currentFilters.fuel_type)    params.fuel_type    = currentFilters.fuel_type;
    if (currentFilters.keyword)      params.keyword      = currentFilters.keyword;
    if (sort)                        params.sort         = sort;

    const data = await api.getSilent('/api/vehicles', params);
    const vehicles = data?.vehicles || [];
    const total    = data?.total    || 0;

    const currentCount = append ? grid.querySelectorAll('.vehicle-card').length + vehicles.length : vehicles.length;

    if (countEl) {
      const catLabel = currentFilters.category ? ` — ${CATEGORY_LABELS[currentFilters.category] || currentFilters.category}` : '';
      countEl.innerHTML = `Showing <strong>${currentCount}</strong> of <strong>${total}</strong> vehicles${catLabel}`;
    }

    if (!vehicles.length && !append) {
      const catName = currentFilters.category ? CATEGORY_LABELS[currentFilters.category] || currentFilters.category : 'vehicles';
      grid.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:80px 20px">
          <svg viewBox="0 0 24 24" width="64" height="64" stroke="var(--muted)" fill="none" stroke-width="2" style="margin:0 auto 24px">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3 style="color:var(--white);margin-bottom:12px">No ${catName} Found</h3>
          <p style="color:var(--muted)">Try adjusting your filters or check back soon — new listings are added regularly.</p>
          <button onclick="clearAllFilters()" class="btn-primary" style="margin-top:24px">Clear Filters</button>
        </div>`;
      return;
    }

    const html = vehicles.map(createVehicleCard).join('');
    if (append) {
      grid.insertAdjacentHTML('beforeend', html);
    } else {
      grid.innerHTML = html;
    }

    const totalShown = grid.querySelectorAll('.vehicle-card').length;
    if (loadMore) {
      loadMore.style.display = totalShown >= total ? 'none' : 'inline-flex';
    }

  } catch (err) {
    console.error('Browse error:', err);
    const catName = currentFilters.category ? CATEGORY_LABELS[currentFilters.category] || currentFilters.category : 'vehicles';
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--muted)">
        <svg viewBox="0 0 24 24" width="56" height="56" stroke="var(--muted)" fill="none" stroke-width="1.5" style="margin:0 auto 20px">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h3 style="color:var(--white);margin-bottom:10px">Could Not Load ${catName}</h3>
        <p style="margin-bottom:20px">There was a problem reaching the server. This may be temporary — please try again.</p>
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
          <button onclick="loadVehicles()" class="btn-primary">🔄 Try Again</button>
          <button onclick="clearAllFilters()" class="btn-ghost">Clear Filters</button>
        </div>
      </div>`;
  }
}

// ── Card builder ──────────────────────────────────────────────────────────────
function createVehicleCard(vehicle) {
  const badgeMap = {
    new_car:   { cls: 'badge-new',   label: 'New' },
    used_car:  { cls: 'badge-used',  label: 'Used' },
    motorbike: { cls: 'badge-bike',  label: 'Motorbike' },
    truck:     { cls: 'badge-truck', label: 'Truck / Bakkie' },
    other:     { cls: 'badge-used',  label: 'Other' },
  };
  const badge = badgeMap[vehicle.category] || { cls: 'badge-used', label: 'Vehicle' };

  const imageUrl = vehicle.images?.[0]
    || 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=600&q=80';

  const verifiedBadge = vehicle.is_verified
    ? '<span class="card-badge badge-featured" style="left:auto;right:12px;top:50px">Verified</span>'
    : '';

  const sellerName = vehicle.contact_name || vehicle.seller_name || 'Seller';
  const initials   = sellerName.substring(0, 2).toUpperCase();

  return `
    <article class="vehicle-card" onclick="window.location='vehicle-detail.html?id=${vehicle.id}'" style="cursor:pointer">
      <div class="card-img">
        <img src="${imageUrl}" alt="${vehicle.year} ${vehicle.make} ${vehicle.model}" loading="lazy"
             onerror="this.src='https://images.unsplash.com/photo-1555215695-3004980ad54e?w=600&q=80'"/>
        <span class="card-badge ${badge.cls}">${badge.label}</span>
        ${verifiedBadge}
        <button class="card-save" onclick="event.stopPropagation();toggleSave(this)" aria-label="Save">
          <svg viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
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
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
          </svg>
          ${vehicle.city || vehicle.province || ''}
        </div>
      </div>
    </article>`;
}
