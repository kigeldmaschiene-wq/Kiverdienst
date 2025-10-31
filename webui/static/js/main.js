// -*- coding: utf-8 -*-
// KIVerdienst V2 - Main JavaScript Utilities

// Toast Notifications
function showToast(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-3 animate-slide-in`;
    toast.innerHTML = `
        <i class="fa-solid ${icons[type]}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
            <i class="fa-solid fa-times"></i>
        </button>
    `;
    
    const container = document.getElementById('toast-container');
    if (container) {
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'error');
}

function showWarning(message) {
    showToast(message, 'warning');
}

function showInfo(message) {
    showToast(message, 'info');
}

// Loading Indicator
function showLoading(element, originalText) {
    if (element) {
        element.disabled = true;
        element.dataset.originalText = originalText || element.innerHTML;
        element.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>L?dt...';
    }
}

function hideLoading(element) {
    if (element) {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || element.innerHTML;
    }
}

// Confirm Dialog
function confirmAction(message) {
    return confirm(message || 'Sind Sie sicher?');
}

// Format Date
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format Number
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return new Intl.NumberFormat('de-DE').format(num);
}

// Format Currency
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '0,00 ?';
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API Helper
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'API Fehler' }));
            throw new Error(error.error || 'API Fehler');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    
    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('hidden');
        });
        
        // Close on outside click (mobile)
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 768 && 
                !sidebar.contains(e.target) && 
                !menuBtn.contains(e.target) &&
                !sidebar.classList.contains('hidden')) {
                sidebar.classList.add('hidden');
            }
        });
    }
});

// Close modal on outside click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop')) {
        const modals = document.querySelectorAll('[id$="Modal"]');
        modals.forEach(modal => {
            if (modal && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
            }
        });
    }
});

// ESC key closes modals
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('[id$="Modal"]');
        modals.forEach(modal => {
            if (modal && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
            }
        });
    }
});

// Add active class to current nav item
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('aside nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('bg-gray-700');
        }
    });
});

// Copy to Clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccess('In Zwischenablage kopiert!');
        }).catch(() => {
            showError('Kopieren fehlgeschlagen');
        });
    } else {
        // Fallback
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showSuccess('In Zwischenablage kopiert!');
    }
}

// Download File
function downloadFile(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Truncate Text
function truncate(text, length) {
    if (!text) return '';
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

// Export to Global Scope
window.showToast = showToast;
window.showSuccess = showSuccess;
window.showError = showError;
window.showWarning = showWarning;
window.showInfo = showInfo;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.confirmAction = confirmAction;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency;
window.debounce = debounce;
window.apiCall = apiCall;
window.copyToClipboard = copyToClipboard;
window.downloadFile = downloadFile;
window.truncate = truncate;
