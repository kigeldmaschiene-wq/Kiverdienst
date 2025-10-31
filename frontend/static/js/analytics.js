// Analytics & Charts

async function loadAnalytics() {
    try {
        const stats = await api('/api/analytics/overview');
        
        const totalViewsEl = document.getElementById('totalViews');
        const monthRevenueEl = document.getElementById('monthRevenue');
        
        if (totalViewsEl) totalViewsEl.textContent = (stats.total_views || 0).toLocaleString();
        if (monthRevenueEl) monthRevenueEl.textContent = '?' + (stats.revenue || 0).toFixed(2);
        
        console.log('? Analytics loaded');
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}
