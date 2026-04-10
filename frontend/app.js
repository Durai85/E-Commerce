import API_URLS from './config.js';

// ── Service URLs (localStorage-backed, editable via ⚙ Config) ────────────────
let PRODUCT_URL = localStorage.getItem('cfg_product_url') || API_URLS.products;
let ORDER_URL   = localStorage.getItem('cfg_order_url')   || API_URLS.orders;
let USER_URL    = localStorage.getItem('cfg_user_url')    || API_URLS.users;

let orderCount = 0;
const SECTION_META = {
  dashboard: { title: 'Dashboard',     sub: 'Overview of all microservices' },
  products:  { title: 'Products',      sub: 'Catalogue from product-service' },
  users:     { title: 'Users',         sub: 'User management via user-service' },
  orders:    { title: 'Orders',        sub: 'Place orders via order-service' },
  health:    { title: 'Health',        sub: 'Kubernetes probe endpoints status' },
  config:    { title: 'Configuration', sub: 'Service endpoint URLs' },
};

// ── Navigation ────────────────────────────────────────────────────────────────
function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  document.getElementById('section-' + name).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => {
    if (n.getAttribute('onclick') && n.getAttribute('onclick').includes("'" + name + "'"))
      n.classList.add('active');
  });

  const meta = SECTION_META[name];
  document.getElementById('page-title').textContent    = meta.title;
  document.getElementById('page-subtitle').textContent = meta.sub;

  // Lazy-load section data
  if (name === 'products') loadProducts();
  if (name === 'users')    loadUsers();
  if (name === 'health')   checkAllHealth();
  if (name === 'config')   loadConfigInputs();
}

// ── Toast Notifications ───────────────────────────────────────────────────────
function toast(type, title, body) {
  const icons = { success: 'bi-check-circle-fill', error: 'bi-x-circle-fill', info: 'bi-info-circle-fill' };
  const colors = { success: '#15803d', error: '#b91c1c', info: '#1d4ed8' };
  const el = document.createElement('div');
  el.className = 'toast-item ' + type;
  el.innerHTML = `
    <i class="bi ${icons[type]}" style="color:${colors[type]};font-size:1.1rem;margin-top:1px"></i>
    <div class="toast-msg">
      <div class="toast-title">${title}</div>
      ${body ? `<div class="toast-body">${body}</div>` : ''}
    </div>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => {
    el.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => el.remove(), 300);
  }, 3500);
}

// ── Avatar helper ─────────────────────────────────────────────────────────────
const AVATAR_COLORS = ['#6d28d9','#1d4ed8','#15803d','#b45309','#be185d','#0f766e'];
function avatarEl(name, idx) {
  const initials = name.split(' ').map(w => w[0]).join('').slice(0,2).toUpperCase();
  const color = AVATAR_COLORS[idx % AVATAR_COLORS.length];
  return `<span class="avatar" style="background:${color}">${initials}</span>`;
}

// ── Health Checks ─────────────────────────────────────────────────────────────
async function checkHealth(url, dotId, badgeId, textId, cardId) {
  const dot    = document.getElementById(dotId);
  const badge  = document.getElementById(badgeId);
  const text   = document.getElementById(textId);
  const card   = document.getElementById(cardId);
  if (dot)   dot.className = 'status-dot checking';
  if (badge) badge.className = 'badge-pill badge-gray';
  if (badge) badge.textContent = 'checking…';
  try {
    const r = await fetch(url + '/health');
    const d = await r.json();
    if (dot)   dot.className   = 'status-dot healthy';
    if (badge) badge.className = 'badge-pill badge-green';
    if (badge) badge.textContent = 'healthy';
    if (text)  text.textContent  = JSON.stringify(d);
    if (card)  card.style.borderColor = '#bbf7d0';
  } catch {
    if (dot)   dot.className   = 'status-dot unhealthy';
    if (badge) badge.className = 'badge-pill badge-red';
    if (badge) badge.textContent = 'unreachable';
    if (text)  text.textContent  = 'Could not connect';
    if (card)  card.style.borderColor = '#fecaca';
  }
}

function checkAllHealth() {
  checkHealth(PRODUCT_URL, 'dot-product', 'hb-product', 'hr-product', 'hc-product');
  checkHealth(ORDER_URL,   'dot-order',   'hb-order',   'hr-order',   'hc-order');
  checkHealth(USER_URL,    'dot-user',    'hb-user',    'hr-user',    'hc-user');
}

// ── Load Products ─────────────────────────────────────────────────────────────
async function loadProducts() {
  const productsLoading = document.getElementById('products-loading');
  const productsTable = document.getElementById('products-table');
  if (!productsLoading || !productsTable) return;

  productsLoading.style.display = '';
  productsTable.style.display   = 'none';
  try {
    const r = await fetch(PRODUCT_URL + '/products');
    const products = await r.json();
    const tbody = document.getElementById('products-body');
    tbody.innerHTML = '';

    products.forEach(p => {
      const stockBadge = p.stock > 50
        ? `<span class="badge-pill badge-green">${p.stock} units</span>`
        : p.stock > 10
        ? `<span class="badge-pill badge-yellow">${p.stock} units</span>`
        : `<span class="badge-pill badge-red">${p.stock} units</span>`;

      tbody.innerHTML += `
        <tr onclick="selectProduct('${p.id}')">
          <td><span class="badge-pill badge-gray">#${p.id}</span></td>
          <td style="font-weight:500">${p.name}</td>
          <td style="font-weight:600;color:#15803d">$${p.price.toFixed(2)}</td>
          <td>${stockBadge}</td>
          <td>
            <button class="btn-outline" style="font-size:0.75rem;padding:0.3rem 0.6rem"
              onclick="event.stopPropagation();selectProduct('${p.id}')">
              <i class="bi bi-cart-plus"></i> Order
            </button>
          </td>
        </tr>`;
    });

    productsLoading.style.display = 'none';
    productsTable.style.display   = '';
    document.getElementById('product-count-badge').textContent = products.length + ' items';
    document.getElementById('dash-products').textContent       = products.length;
  } catch {
    productsLoading.innerHTML = `
      <div style="padding:2.5rem;text-align:center;color:#b91c1c">
        <i class="bi bi-exclamation-triangle" style="font-size:2rem;display:block;margin-bottom:0.5rem"></i>
        Cannot reach product-service
      </div>`;
  }
}

function selectProduct(id) {
  document.getElementById('order-product-id').value = id;
  showSection('orders');
  toast('info', 'Product selected', 'Product #' + id + ' is ready to order');
}

// ── Load Users ────────────────────────────────────────────────────────────────
async function loadUsers() {
  const usersLoading = document.getElementById('users-loading');
  const usersTable = document.getElementById('users-table');
  if (!usersLoading || !usersTable) return;

  usersLoading.style.display = '';
  usersTable.style.display   = 'none';
  try {
    const r = await fetch(USER_URL + '/users');
    const users = await r.json();
    const tbody = document.getElementById('users-body');
    tbody.innerHTML = '';

    users.forEach((u, i) => {
      const roleBadge = u.role === 'admin'
        ? `<span class="badge-pill badge-purple">admin</span>`
        : `<span class="badge-pill badge-blue">customer</span>`;
      tbody.innerHTML += `
        <tr>
          <td>
            <div style="display:flex;align-items:center;gap:0.6rem">
              ${avatarEl(u.name, i)}
              <div>
                <div style="font-weight:500;font-size:0.875rem">${u.name}</div>
                <div style="font-size:0.72rem;color:var(--muted)">${u.id}</div>
              </div>
            </div>
          </td>
          <td style="font-size:0.85rem;color:var(--muted)">${u.email}</td>
          <td>${roleBadge}</td>
        </tr>`;
    });

    usersLoading.style.display = 'none';
    usersTable.style.display   = '';
    document.getElementById('user-count-badge').textContent = users.length + ' users';
    document.getElementById('dash-users').textContent       = users.length;
  } catch {
    usersLoading.innerHTML = `
      <div style="padding:2.5rem;text-align:center;color:#b91c1c">
        <i class="bi bi-exclamation-triangle" style="font-size:2rem;display:block;margin-bottom:0.5rem"></i>
        Cannot reach user-service
      </div>`;
  }
}

// ── Register User ─────────────────────────────────────────────────────────────
async function registerUser() {
  const name    = document.getElementById('reg-name').value.trim();
  const email   = document.getElementById('reg-email').value.trim();
  const role    = document.getElementById('reg-role').value;
  const result  = document.getElementById('reg-result');
  result.innerHTML = '';

  if (!name || !email) {
    result.innerHTML = `<div class="alert alert-warning"><i class="bi bi-exclamation-circle"></i>Please fill in name and email.</div>`;
    return;
  }

  result.innerHTML = `<div class="alert alert-info"><span class="spinner" style="width:14px;height:14px"></span> Registering…</div>`;
  try {
    const r = await fetch(USER_URL + '/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, role }),
    });
    const d = await r.json();
    if (r.ok) {
      result.innerHTML = `
        <div class="alert alert-success">
          <i class="bi bi-check-circle-fill"></i>
          <div><strong>${d.name}</strong> registered as <em>${d.role}</em></div>
        </div>`;
      document.getElementById('reg-name').value  = '';
      document.getElementById('reg-email').value = '';
      toast('success', 'User registered', d.name + ' (' + d.email + ')');
      loadUsers();
    } else {
      result.innerHTML = `<div class="alert alert-danger"><i class="bi bi-x-circle-fill"></i>${d.error}</div>`;
    }
  } catch {
    result.innerHTML = `<div class="alert alert-danger"><i class="bi bi-x-circle-fill"></i>Cannot reach user-service</div>`;
  }
}

// ── Place Order ───────────────────────────────────────────────────────────────
async function placeOrder() {
  const productId = document.getElementById('order-product-id').value.trim();
  const result    = document.getElementById('order-result');
  const btn       = document.getElementById('order-btn');
  result.innerHTML = '';

  if (!productId) {
    result.innerHTML = `<div class="alert alert-warning"><i class="bi bi-exclamation-circle"></i>Please enter a product ID.</div>`;
    return;
  }

  btn.disabled = true;
  result.innerHTML = `<div class="alert alert-info"><span class="spinner" style="width:14px;height:14px"></span> Contacting order-service…</div>`;

  try {
    const r = await fetch(ORDER_URL + '/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId }),
    });
    const d = await r.json();

    if (r.ok) {
      orderCount++;
      document.getElementById('dash-orders').textContent       = orderCount;
      document.getElementById('order-count-badge').textContent = orderCount + ' orders';
      document.getElementById('order-history-empty').style.display = 'none';

      result.innerHTML = `
        <div class="alert alert-success">
          <i class="bi bi-check-circle-fill"></i>
          <div><strong>Order #${d.order_id} confirmed!</strong><br>
          <span style="font-size:0.78rem">${d.product_name} — $${d.unit_price?.toFixed(2)}</span></div>
        </div>`;

      // Add to order history
      const item = document.createElement('div');
      item.className = 'order-item';
      item.innerHTML = `
        <div style="display:flex;align-items:center;gap:0.75rem">
          <div style="width:36px;height:36px;background:#dcfce7;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#15803d">
            <i class="bi bi-bag-check"></i>
          </div>
          <div>
            <div style="font-weight:500;font-size:0.875rem">${d.product_name}</div>
            <div style="font-size:0.72rem;color:var(--muted)">Order #${d.order_id} · $${d.unit_price?.toFixed(2)}</div>
          </div>
        </div>
        <span class="badge-pill badge-green">confirmed</span>`;
      document.getElementById('order-history-list').prepend(item);

      document.getElementById('order-product-id').value = '';
      toast('success', 'Order confirmed', d.product_name + ' — $' + d.unit_price?.toFixed(2));
    } else {
      result.innerHTML = `<div class="alert alert-danger"><i class="bi bi-x-circle-fill"></i>${d.error}</div>`;
      toast('error', 'Order failed', d.error);
    }
  } catch {
    result.innerHTML = `<div class="alert alert-danger"><i class="bi bi-x-circle-fill"></i>Cannot reach order-service</div>`;
    toast('error', 'Connection error', 'order-service is unreachable');
  } finally {
    btn.disabled = false;
  }
}

// ── Config Management ─────────────────────────────────────────────────────────
function updateActiveEndpoints() {
  document.getElementById('active-product').textContent = PRODUCT_URL;
  document.getElementById('active-order').textContent   = ORDER_URL;
  document.getElementById('active-user').textContent    = USER_URL;
}

function loadConfigInputs() {
  document.getElementById('cfg-product').value = PRODUCT_URL;
  document.getElementById('cfg-order').value   = ORDER_URL;
  document.getElementById('cfg-user').value    = USER_URL;
  updateActiveEndpoints();
}

function saveConfig() {
  const p = (document.getElementById('cfg-product').value || '').trim().replace(/\/$/, '');
  const o = (document.getElementById('cfg-order').value   || '').trim().replace(/\/$/, '');
  const u = (document.getElementById('cfg-user').value    || '').trim().replace(/\/$/, '');
  const result = document.getElementById('cfg-result');

  if (!p || !o || !u) {
    result.innerHTML = '<div class="alert alert-warning"><i class="bi bi-exclamation-circle"></i>All three URLs are required.</div>';
    return;
  }
  localStorage.setItem('cfg_product_url', p);
  localStorage.setItem('cfg_order_url',   o);
  localStorage.setItem('cfg_user_url',    u);
  PRODUCT_URL = p; ORDER_URL = o; USER_URL = u;
  updateActiveEndpoints();
  result.innerHTML = '<div class="alert alert-success"><i class="bi bi-check-circle-fill"></i>URLs saved — services will use the new endpoints.</div>';
  toast('success', 'Config saved', 'Service URLs updated');
  checkAllHealth();
}

function resetConfig() {
  localStorage.removeItem('cfg_product_url');
  localStorage.removeItem('cfg_order_url');
  localStorage.removeItem('cfg_user_url');
  PRODUCT_URL = API_URLS.products;
  ORDER_URL   = API_URLS.orders;
  USER_URL    = API_URLS.users;
  loadConfigInputs();
  document.getElementById('cfg-result').innerHTML =
    '<div class="alert alert-info"><i class="bi bi-info-circle"></i>Reset to defaults.</div>';
  toast('info', 'Config reset', 'Using defaults');
}

// ── Global Refresh ────────────────────────────────────────────────────────────
function refreshAll() {
  checkAllHealth();
  loadProducts();
  loadUsers();
  toast('info', 'Refreshing', 'Reloading all service data…');
}

// Attach functions to window for onclick handlers in HTML
window.showSection = showSection;
window.refreshAll = refreshAll;
window.loadProducts = loadProducts;
window.loadUsers = loadUsers;
window.registerUser = registerUser;
window.placeOrder = placeOrder;
window.saveConfig = saveConfig;
window.resetConfig = resetConfig;
window.selectProduct = selectProduct;
window.checkAllHealth = checkAllHealth;

// ── Init ──────────────────────────────────────────────────────────────────────
updateActiveEndpoints();
checkAllHealth();
loadProducts();
loadUsers();