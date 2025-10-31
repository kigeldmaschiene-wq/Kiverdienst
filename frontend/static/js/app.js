// KIVerdienst v2 - Main JavaScript

// CRITICAL: Dynamic backend URL
const BACKEND_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : `http://${window.location.hostname}:8000`;

console.log('?? KIVerdienst v2 Frontend Loaded');
console.log('?? Backend URL:', BACKEND_URL);

// API Helper
async function api(url, options = {}) {
    try {
        const response = await fetch(`${BACKEND_URL}${url}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API Error');
        }
        
        return await response.json();
    } catch (error) {
        console.error('? API failed:', error);
        showError(error.message);
        throw error;
    }
}

// Show Error
function showError(message) {
    const el = document.getElementById('error');
    if (el) {
        el.textContent = message;
        el.style.display = 'block';
    } else {
        alert('Error: ' + message);
    }
}

// Show Success
function showSuccess(message) {
    const el = document.getElementById('success');
    if (el) {
        el.textContent = message;
        el.style.display = 'block';
        setTimeout(() => {
            el.style.display = 'none';
        }, 3000);
    }
}

// Setup
async function startSetup() {
    try {
        const btn = document.querySelector('.btn-primary');
        btn.disabled = true;
        btn.textContent = 'Setting up...';
        
        const result = await api('/api/setup/init', {method: 'POST'});
        
        if (result.success) {
            showSuccess('Setup complete! Redirecting...');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        }
    } catch (error) {
        console.error('Setup failed:', error);
        const btn = document.querySelector('.btn-primary');
        btn.disabled = false;
        btn.textContent = 'Start Setup';
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const stats = await api('/api/analytics/overview');
        
        const brandsEl = document.getElementById('brandsCount');
        const videosEl = document.getElementById('videosCount');
        const viewsEl = document.getElementById('viewsCount');
        const revenueEl = document.getElementById('revenue');
        
        if (brandsEl) brandsEl.textContent = stats.brands || 0;
        if (videosEl) videosEl.textContent = stats.videos || 0;
        if (viewsEl) viewsEl.textContent = (stats.total_views || 0).toLocaleString();
        if (revenueEl) revenueEl.textContent = '?' + (stats.revenue || 0).toFixed(2);
        
        console.log('? Dashboard loaded:', stats);
    } catch (error) {
        console.error('? Failed to load dashboard:', error);
    }
}

// Characters
async function loadCharacters() {
    try {
        const characters = await api('/api/characters');
        const container = document.getElementById('charactersList');
        
        if (!container) return;
        
        if (characters.length === 0) {
            container.innerHTML = '<p>No characters yet. Create your first character!</p>';
            return;
        }
        
        container.innerHTML = characters.map(char => `
            <div class="list-item">
                <h3>${char.name}</h3>
                <p>Type: ${char.character_type || 'N/A'} | Gender: ${char.gender || 'N/A'}</p>
                <p>${char.description || ''}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load characters:', error);
    }
}

// Accounts
async function loadAccounts() {
    try {
        const accounts = await api('/api/accounts');
        const container = document.getElementById('accountsList');
        
        if (!container) return;
        
        if (accounts.length === 0) {
            container.innerHTML = '<p>No accounts yet. Add your first social media account!</p>';
            return;
        }
        
        container.innerHTML = accounts.map(acc => `
            <div class="list-item">
                <h3>${acc.platform}: @${acc.username}</h3>
                <p>Status: ${acc.status} | Followers: ${acc.followers || 0}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load accounts:', error);
    }
}

// Products
async function loadProducts() {
    try {
        const products = await api('/api/products');
        const container = document.getElementById('productsList');
        
        if (!container) return;
        
        if (products.length === 0) {
            container.innerHTML = '<p>No products yet. Add your first product!</p>';
            return;
        }
        
        container.innerHTML = products.map(prod => `
            <div class="list-item">
                <h3>${prod.name}</h3>
                <p>Price: ?${prod.price || 0} | Commission: ${(prod.commission_rate * 100) || 0}%</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}

// Leads
async function loadLeads() {
    try {
        const leads = await api('/api/leads');
        const container = document.getElementById('leadsList');
        
        if (!container) return;
        
        if (leads.length === 0) {
            container.innerHTML = '<p>No leads yet.</p>';
            return;
        }
        
        const totalEl = document.getElementById('totalLeads');
        if (totalEl) totalEl.textContent = leads.length;
        
        const activeLeads = leads.filter(l => l.status === 'active');
        const activeEl = document.getElementById('activeLeads');
        if (activeEl) activeEl.textContent = activeLeads.length;
        
        container.innerHTML = leads.map(lead => `
            <div class="list-item">
                <h3>${lead.name || lead.email}</h3>
                <p>${lead.email} | Status: ${lead.status}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load leads:', error);
    }
}

// Utility: Add Account
function addAccount() {
    alert('Add Account feature coming soon!');
}

// Utility: Add Product
function addProduct() {
    alert('Add Product feature coming soon!');
}

// Utility: Add Lead
function addLead() {
    alert('Add Lead feature coming soon!');
}

// Utility: Generate Video
function generateVideo() {
    alert('Video generation feature coming soon!');
}

// Utility: Show Create Character Modal
function showCreateCharacterModal() {
    alert('Create Character feature coming soon!');
}

console.log('? App.js loaded');
