// Videos Management

async function loadVideos() {
    try {
        const videos = await api('/api/videos');
        const container = document.getElementById('videosList');
        
        if (!container) return;
        
        if (videos.length === 0) {
            container.innerHTML = '<p>No videos yet. Generate your first video!</p>';
            return;
        }
        
        container.innerHTML = videos.map(video => `
            <div class="list-item video-item">
                <div class="video-header">
                    <h3>${video.title}</h3>
                    <span class="badge badge-${getStatusColor(video.status)}">
                        ${video.status}
                    </span>
                </div>
                <p>Platform: ${video.platform || 'N/A'}</p>
                <div class="video-stats">
                    <span>??? ${video.views || 0}</span>
                    <span>?? ${video.likes || 0}</span>
                    <span>?? ${video.comments || 0}</span>
                    <span>?? ${video.shares || 0}</span>
                </div>
                ${video.is_viral ? '<span class="badge badge-success">?? VIRAL</span>' : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load videos:', error);
    }
}

function getStatusColor(status) {
    const colors = {
        'draft': 'secondary',
        'processing': 'warning',
        'ready': 'success',
        'posted': 'primary',
        'failed': 'danger'
    };
    return colors[status] || 'secondary';
}

function filterVideos() {
    const statusFilter = document.getElementById('statusFilter').value;
    const platformFilter = document.getElementById('platformFilter').value;
    console.log('Filtering:', statusFilter, platformFilter);
    // Future: Implement filtering logic
}
