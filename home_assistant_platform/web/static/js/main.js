// Main JavaScript for Home Assistant Platform

// Utility functions
function showNotification(message, type = 'info') {
    // Use toast system if available, otherwise fallback
    if (typeof toast !== 'undefined') {
        toast.show(message, type);
    } else {
        alert(message);
    }
}

function showSuccess(message) {
    if (typeof toast !== 'undefined') {
        toast.success(message);
    } else {
        alert(message);
    }
}

function showError(message) {
    if (typeof toast !== 'undefined') {
        toast.error(message);
    } else {
        alert(message);
    }
}

function showLoading(element) {
    if (element) {
        element.classList.add('btn-loading');
        element.disabled = true;
    }
}

function hideLoading(element) {
    if (element) {
        element.classList.remove('btn-loading');
        element.disabled = false;
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// API helper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options,
            body: options.body ? options.body : undefined
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        }
        
        // Handle empty responses
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        return {};
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Home Assistant Platform UI loaded');
});

