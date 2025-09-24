/**
 * Real-time Dashboard Updates
 * Automatically updates dashboard statistics every 30 seconds
 */

class DashboardRealtime {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.isUpdating = false;
        this.updateTimer = null;
        this.apiEndpoint = '/api/job-orders/dashboard-stats/';
        
        this.init();
    }
    
    init() {
        // Start the real-time updates
        this.startUpdates();
        
        // Add visual indicators for updates
        this.addUpdateIndicators();
        
        // Handle page visibility changes to pause/resume updates
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }
    
    startUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
        
        this.updateTimer = setInterval(() => {
            this.updateDashboard();
        }, this.updateInterval);
        
        console.log('Dashboard real-time updates started');
    }
    
    pauseUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        console.log('Dashboard real-time updates paused');
    }
    
    resumeUpdates() {
        if (!this.updateTimer) {
            this.startUpdates();
        }
        console.log('Dashboard real-time updates resumed');
    }
    
    async updateDashboard() {
        if (this.isUpdating) {
            return; // Prevent overlapping requests
        }
        
        this.isUpdating = true;
        this.showUpdateIndicator();
        
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.updateDashboardCards(data.data);
                this.showSuccessIndicator();
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('Dashboard update failed:', error);
            this.showErrorIndicator();
        } finally {
            this.isUpdating = false;
            this.hideUpdateIndicator();
        }
    }
    
    updateDashboardCards(data) {
        // Update Total Products
        this.updateCardValue('[data-stat="product_count"] .font-weight-bolder', data.product_count);
        
        // Update Active Customers
        this.updateCardValue('[data-stat="customer_count"] .font-weight-bolder', data.customer_count);
        
        // Update Total Orders
        this.updateCardValue('[data-stat="order_count"] .font-weight-bolder', data.order_count);
        
        // Update Pending Orders
        this.updateCardValue('[data-stat="pending_count"] .font-weight-bolder', data.pending_count);
        
        console.log('Dashboard cards updated:', data);
    }
    
    updateCardValue(selector, newValue) {
        const element = document.querySelector(selector);
        
        if (element) {
            // Check if the value has actually changed
            const currentValue = element.textContent.trim();
            if (currentValue === newValue.toString()) {
                return; // No need to update if value is the same
            }
            
            // Add smooth transition effect
            element.style.transition = 'all 0.3s ease';
            element.style.transform = 'scale(1.1)';
            
            setTimeout(() => {
                element.textContent = newValue;
                element.setAttribute('data-value', newValue);
                element.style.transform = 'scale(1)';
            }, 150);
        } else {
            console.warn(`Element not found for selector: ${selector}`);
        }
    }
    
    addUpdateIndicators() {
        // Add a small indicator to show when updates are happening
        const indicator = document.createElement('div');
        indicator.id = 'dashboard-update-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #28a745;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 9999;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        `;
        document.body.appendChild(indicator);
    }
    
    showUpdateIndicator() {
        const indicator = document.getElementById('dashboard-update-indicator');
        if (indicator) {
            indicator.style.backgroundColor = '#ffc107';
            indicator.style.opacity = '1';
        }
    }
    
    showSuccessIndicator() {
        const indicator = document.getElementById('dashboard-update-indicator');
        if (indicator) {
            indicator.style.backgroundColor = '#28a745';
            setTimeout(() => {
                indicator.style.opacity = '0';
            }, 1000);
        }
    }
    
    showErrorIndicator() {
        const indicator = document.getElementById('dashboard-update-indicator');
        if (indicator) {
            indicator.style.backgroundColor = '#dc3545';
            setTimeout(() => {
                indicator.style.opacity = '0';
            }, 2000);
        }
    }
    
    hideUpdateIndicator() {
        const indicator = document.getElementById('dashboard-update-indicator');
        if (indicator) {
            indicator.style.opacity = '0';
        }
    }
    
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    // Public method to manually trigger an update
    forceUpdate() {
        this.updateDashboard();
    }
    
    // Public method to change update interval
    setUpdateInterval(interval) {
        this.updateInterval = interval;
        this.startUpdates();
    }
    
    // Cleanup method
    destroy() {
        this.pauseUpdates();
        const indicator = document.getElementById('dashboard-update-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on job orders pages
    if (window.location.pathname.includes('/job-orders/')) {
        window.dashboardRealtime = new DashboardRealtime();
        
        // Add keyboard shortcut for manual update (Ctrl+Shift+R)
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                e.preventDefault();
                window.dashboardRealtime.forceUpdate();
            }
        });
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboardRealtime) {
        window.dashboardRealtime.destroy();
    }
});
