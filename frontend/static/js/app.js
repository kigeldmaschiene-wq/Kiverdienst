// CRITICAL: Dynamic BACKEND_URL - DO NOT HARDCODE!
// This fixes the previous system's failure where 'http://backend:8000' was hardcoded
const BACKEND_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : `http://${window.location.hostname}:8000`;

console.log('Backend URL:', BACKEND_URL);

// API helper function
async function api(endpoint, options = {}) {
    try {
        const response = await fetch(`${BACKEND_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'API Fehler' }));
            throw new Error(error.detail || 'API Fehler');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification(`Fehler: ${error.message}`, 'error');
        throw error;
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
        type === 'error' ? 'bg-red-500' : 
        type === 'success' ? 'bg-green-500' : 
        'bg-blue-500'
    } text-white`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Setup functions
async function startSetup() {
    try {
        const result = await api('/api/setup/init', { method: 'POST' });
        if (result.success) {
            showNotification('Setup erfolgreich abgeschlossen!', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        }
    } catch (error) {
        console.error('Setup failed:', error);
    }
}

// Dashboard functions
async function loadDashboard() {
    try {
        const stats = await api('/api/analytics/overview');
        
        document.getElementById('brandsCount').textContent = stats.brands || 0;
        document.getElementById('videosCount').textContent = stats.videos || 0;
        document.getElementById('totalViews').textContent = (stats.total_views || 0).toLocaleString('de-DE');
        document.getElementById('revenue').textContent = `${(stats.revenue || 0).toFixed(2)}?`;
        
        // Load recent videos
        if (stats.recent_videos && stats.recent_videos.length > 0) {
            const container = document.getElementById('recentVideos');
            if (container) {
                container.innerHTML = stats.recent_videos.slice(0, 5).map(video => `
                    <div class="flex items-center justify-between py-2 border-b">
                        <div>
                            <p class="font-medium">${video.title || 'Ohne Titel'}</p>
                            <p class="text-sm text-gray-500">${video.brand_name || 'Unbekannt'}</p>
                        </div>
                        <span class="text-sm text-gray-600">${video.views || 0} Views</span>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Dashboard load failed:', error);
    }
}

// Brands functions
async function loadBrands() {
    try {
        const brands = await api('/api/brands');
        const container = document.getElementById('brandsContainer');
        
        if (!container) return;
        
        if (brands.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">Keine Marken vorhanden. Erstelle deine erste Marke!</p>';
            return;
        }
        
        container.innerHTML = brands.map(brand => `
            <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
                <div class="flex items-start justify-between mb-4">
                    <div>
                        <h3 class="text-xl font-bold text-gray-900">${brand.name}</h3>
                        <p class="text-gray-600">${brand.niche || 'Keine Nische'}</p>
                    </div>
                    <span class="px-3 py-1 text-sm rounded-full ${
                        brand.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }">
                        ${brand.active ? 'Aktiv' : 'Inaktiv'}
                    </span>
                </div>
                <p class="text-gray-700 mb-4">${brand.description || 'Keine Beschreibung'}</p>
                <div class="flex gap-2 text-sm mb-4">
                    ${brand.tiktok_enabled ? '<span class="px-2 py-1 bg-black text-white rounded">TikTok</span>' : ''}
                    ${brand.instagram_enabled ? '<span class="px-2 py-1 bg-pink-500 text-white rounded">Instagram</span>' : ''}
                    ${brand.youtube_enabled ? '<span class="px-2 py-1 bg-red-500 text-white rounded">YouTube</span>' : ''}
                </div>
                <div class="text-sm text-gray-600 mb-4">
                    <p>Characters: ${brand.character_count || 0}</p>
                    <p>Videos: ${brand.video_count || 0}</p>
                </div>
                <div class="flex gap-2">
                    <button onclick="editBrand(${brand.id})" class="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Bearbeiten
                    </button>
                    <button onclick="toggleBrand(${brand.id})" class="flex-1 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
                        ${brand.active ? 'Deaktivieren' : 'Aktivieren'}
                    </button>
                    <button onclick="deleteBrand(${brand.id})" class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">
                        L?schen
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Brands load failed:', error);
    }
}

async function createBrand(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    const brandData = {
        name: formData.get('name'),
        niche: formData.get('niche'),
        description: formData.get('description'),
        active: formData.get('active') === 'on',
        videos_per_day: parseInt(formData.get('videos_per_day')) || 7
    };
    
    try {
        await api('/api/brands', {
            method: 'POST',
            body: JSON.stringify(brandData)
        });
        
        showNotification('Marke erfolgreich erstellt!', 'success');
        form.reset();
        await loadBrands();
    } catch (error) {
        console.error('Brand creation failed:', error);
    }
}

async function deleteBrand(brandId) {
    if (!confirm('Marke wirklich l?schen? Alle zugeh?rigen Daten werden gel?scht!')) {
        return;
    }
    
    try {
        await api(`/api/brands/${brandId}`, { method: 'DELETE' });
        showNotification('Marke gel?scht!', 'success');
        await loadBrands();
    } catch (error) {
        console.error('Brand deletion failed:', error);
    }
}

async function toggleBrand(brandId) {
    try {
        await api(`/api/brands/${brandId}/toggle`, { method: 'PATCH' });
        showNotification('Status ge?ndert!', 'success');
        await loadBrands();
    } catch (error) {
        console.error('Brand toggle failed:', error);
    }
}

// Videos functions
async function loadVideos() {
    try {
        const videos = await api('/api/videos?limit=50');
        const container = document.getElementById('videosContainer');
        
        if (!container) return;
        
        if (videos.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">Keine Videos vorhanden.</p>';
            return;
        }
        
        container.innerHTML = videos.map(video => `
            <div class="bg-white p-4 rounded-lg shadow">
                <div class="flex items-start justify-between mb-2">
                    <h4 class="font-semibold">${video.title || 'Ohne Titel'}</h4>
                    <span class="px-2 py-1 text-xs rounded ${
                        video.status === 'approved' ? 'bg-green-100 text-green-800' :
                        video.status === 'generating' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                    }">
                        ${video.status}
                    </span>
                </div>
                <p class="text-sm text-gray-600 mb-2">${video.brand_name || 'Unbekannt'}</p>
                <div class="flex gap-4 text-sm text-gray-600 mb-3">
                    <span>?? ${video.views || 0}</span>
                    <span>?? ${video.likes || 0}</span>
                    <span>?? ${video.comments || 0}</span>
                </div>
                <div class="flex gap-2">
                    ${video.status === 'draft' ? `<button onclick="approveVideo(${video.id})" class="px-3 py-1 bg-green-500 text-white text-sm rounded">Freigeben</button>` : ''}
                    <button onclick="deleteVideo(${video.id})" class="px-3 py-1 bg-red-500 text-white text-sm rounded">L?schen</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Videos load failed:', error);
    }
}

async function generateVideo(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    const videoData = {
        brand_id: parseInt(formData.get('brand_id')),
        topic: formData.get('topic'),
        platform: formData.get('platform') || 'tiktok'
    };
    
    try {
        const result = await api('/api/videos/generate', {
            method: 'POST',
            body: JSON.stringify(videoData)
        });
        
        showNotification('Video-Generierung gestartet!', 'success');
        form.reset();
        setTimeout(() => loadVideos(), 2000);
    } catch (error) {
        console.error('Video generation failed:', error);
    }
}

async function approveVideo(videoId) {
    try {
        await api(`/api/videos/${videoId}/approve`, { method: 'PATCH' });
        showNotification('Video freigegeben!', 'success');
        await loadVideos();
    } catch (error) {
        console.error('Video approval failed:', error);
    }
}

async function deleteVideo(videoId) {
    if (!confirm('Video wirklich l?schen?')) return;
    
    try {
        await api(`/api/videos/${videoId}`, { method: 'DELETE' });
        showNotification('Video gel?scht!', 'success');
        await loadVideos();
    } catch (error) {
        console.error('Video deletion failed:', error);
    }
}

// Export functions to window
window.api = api;
window.startSetup = startSetup;
window.loadDashboard = loadDashboard;
window.loadBrands = loadBrands;
window.createBrand = createBrand;
window.deleteBrand = deleteBrand;
window.toggleBrand = toggleBrand;
window.loadVideos = loadVideos;
window.generateVideo = generateVideo;
window.approveVideo = approveVideo;
window.deleteVideo = deleteVideo;
