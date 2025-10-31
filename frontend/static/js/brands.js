// Brands Management

async function loadBrands() {
    try {
        const brands = await api('/api/brands');
        const container = document.getElementById('brandsList');
        
        if (!container) return;
        
        if (brands.length === 0) {
            container.innerHTML = '<p>No brands yet. Create your first brand to get started!</p>';
            return;
        }
        
        container.innerHTML = brands.map(brand => `
            <div class="list-item brand-item">
                <div class="brand-header">
                    <h3>${brand.name}</h3>
                    <span class="badge ${brand.active ? 'badge-success' : 'badge-secondary'}">
                        ${brand.active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <p class="brand-niche">${brand.niche || 'No niche specified'}</p>
                <p class="brand-description">${brand.description || ''}</p>
                <div class="brand-platforms">
                    ${brand.tiktok_enabled ? '?? TikTok' : ''}
                    ${brand.instagram_enabled ? '?? Instagram' : ''}
                    ${brand.youtube_enabled ? '?? YouTube' : ''}
                </div>
                <div class="brand-actions">
                    <button onclick="editBrand(${brand.id})" class="btn btn-sm">Edit</button>
                    <button onclick="deleteBrand(${brand.id})" class="btn btn-sm btn-danger">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load brands:', error);
    }
}

function showCreateBrandModal() {
    document.getElementById('createBrandModal').style.display = 'flex';
}

function hideCreateBrandModal() {
    document.getElementById('createBrandModal').style.display = 'none';
}

document.getElementById('createBrandForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    try {
        const data = {
            name: document.getElementById('brandName').value,
            niche: document.getElementById('brandNiche').value,
            description: document.getElementById('brandDescription').value
        };
        
        const result = await api('/api/brands', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        if (result.success) {
            showSuccess('Brand created successfully!');
            hideCreateBrandModal();
            loadBrands();
            e.target.reset();
        }
    } catch (error) {
        console.error('Failed to create brand:', error);
    }
});

async function editBrand(id) {
    alert(`Edit brand ${id} - Coming soon!`);
}

async function deleteBrand(id) {
    if (!confirm('Are you sure you want to delete this brand?')) return;
    
    try {
        await api(`/api/brands/${id}`, {method: 'DELETE'});
        showSuccess('Brand deleted successfully!');
        loadBrands();
    } catch (error) {
        console.error('Failed to delete brand:', error);
    }
}
