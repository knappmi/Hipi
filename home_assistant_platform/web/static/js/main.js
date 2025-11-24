// Main JavaScript for Home Assistant Platform

// Utility functions
function showNotification(message, type = 'info') {
    // Simple notification - can be enhanced with a toast library
    alert(message);
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
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Home Assistant Platform UI loaded');
});

