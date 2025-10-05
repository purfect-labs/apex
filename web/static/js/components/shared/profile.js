/*!
 * APEX Profile & License Management Component
 * Handles license activation, subscription management, and user profile
 * Following APEX shared component pattern
 */

window.APEX = window.APEX || {};

// Profile Management Module
window.APEX.Profile = {
    // State management
    currentLicense: null,
    subscriptionInfo: null,
    
    // Initialize profile component
    init() {
        console.log('🔑 Initializing APEX Profile component...');
        this.bindEvents();
        this.loadInitialData();
    },
    
    // Event bindings
    bindEvents() {
        // License activation form
        const activateBtn = document.getElementById('activate-license-btn');
        if (activateBtn) {
            activateBtn.addEventListener('click', this.handleLicenseActivation.bind(this));
        }
        
        // Trial license generation
        const trialBtn = document.getElementById('generate-trial-btn');
        if (trialBtn) {
            trialBtn.addEventListener('click', this.handleTrialGeneration.bind(this));
        }
        
        // License deactivation
        const deactivateBtn = document.getElementById('deactivate-license-btn');
        if (deactivateBtn) {
            deactivateBtn.addEventListener('click', this.handleLicenseDeactivation.bind(this));
        }
        
        // Copy license key button
        const copyBtns = document.querySelectorAll('.copy-license-key');
        copyBtns.forEach(btn => {
            btn.addEventListener('click', this.copyLicenseKey.bind(this));
        });
        
        // Refresh license status
        const refreshBtn = document.getElementById('refresh-license-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.refreshLicenseStatus.bind(this));
        }
    },
    
    // Load initial profile data
    async loadInitialData() {
        try {
            await this.fetchLicenseStatus();
            await this.fetchSubscriptionInfo();
            this.updateUI();
        } catch (error) {
            console.error('Failed to load initial profile data:', error);
            this.showError('Failed to load profile data');
        }
    },
    
    // Fetch current license status
    async fetchLicenseStatus() {
        try {
            const response = await fetch('/api/license/status');
            const data = await response.json();
            
            if (data.success !== false) {
                this.currentLicense = data;
                console.log('✅ License status loaded:', data);
            } else {
                console.log('ℹ️ No active license found');
                this.currentLicense = data;
            }
        } catch (error) {
            console.error('Failed to fetch license status:', error);
            throw error;
        }
    },
    
    // Fetch subscription information
    async fetchSubscriptionInfo() {
        try {
            const response = await fetch('/api/license/subscription');
            const data = await response.json();
            
            if (data.success !== false) {
                this.subscriptionInfo = data;
                console.log('✅ Subscription info loaded:', data);
            } else {
                console.log('ℹ️ No subscription info available');
            }
        } catch (error) {
            console.error('Failed to fetch subscription info:', error);
            // Don't throw - subscription info is optional
        }
    },
    
    // Handle license activation
    async handleLicenseActivation() {
        const licenseKey = document.getElementById('license-key-input')?.value.trim();
        const userEmail = document.getElementById('user-email-input')?.value.trim();
        
        if (!licenseKey) {
            this.showError('Please enter a license key');
            return;
        }
        
        try {
            this.setLoading(true, 'Activating license...');
            
            const response = await fetch('/api/license/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    license_key: licenseKey,
                    user_email: userEmail || null
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('License activation started. Check terminal for progress...');
                // Clear form
                document.getElementById('license-key-input').value = '';
                if (document.getElementById('user-email-input')) {
                    document.getElementById('user-email-input').value = '';
                }
            } else {
                this.showError(data.error || 'License activation failed');
            }
            
        } catch (error) {
            console.error('License activation failed:', error);
            this.showError('License activation failed: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    },
    
    // Handle trial license generation
    async handleTrialGeneration() {
        const userEmail = document.getElementById('trial-email-input')?.value.trim();
        const days = parseInt(document.getElementById('trial-days-input')?.value) || 7;
        
        if (!userEmail) {
            this.showError('Please enter an email address');
            return;
        }
        
        if (!this.isValidEmail(userEmail)) {
            this.showError('Please enter a valid email address');
            return;
        }
        
        try {
            this.setLoading(true, 'Generating trial license...');
            
            const response = await fetch('/api/license/generate-trial', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_email: userEmail,
                    days: days
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Trial license generation started. Check terminal for your ${days}-day license key...`);
                // Clear form
                document.getElementById('trial-email-input').value = '';
            } else {
                this.showError(data.error || 'Trial license generation failed');
            }
            
        } catch (error) {
            console.error('Trial license generation failed:', error);
            this.showError('Trial license generation failed: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    },
    
    // Handle license deactivation
    async handleLicenseDeactivation() {
        if (!confirm('Are you sure you want to deactivate your license? This will remove it from your system.')) {
            return;
        }
        
        try {
            this.setLoading(true, 'Deactivating license...');
            
            const response = await fetch('/api/license/deactivate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('License deactivation started. Check terminal for confirmation...');
                // Refresh status after a delay
                setTimeout(() => {
                    this.refreshLicenseStatus();
                }, 2000);
            } else {
                this.showError(data.error || 'License deactivation failed');
            }
            
        } catch (error) {
            console.error('License deactivation failed:', error);
            this.showError('License deactivation failed: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    },
    
    // Copy license key to clipboard
    async copyLicenseKey(event) {
        const button = event.target.closest('.copy-license-key');
        const licenseKey = button.dataset.licenseKey;
        
        if (!licenseKey) {
            this.showError('No license key to copy');
            return;
        }
        
        try {
            await navigator.clipboard.writeText(licenseKey);
            
            // Visual feedback
            const originalText = button.textContent;
            button.textContent = '✓ Copied!';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copied');
            }, 2000);
            
        } catch (error) {
            console.error('Failed to copy license key:', error);
            this.showError('Failed to copy license key');
        }
    },
    
    // Refresh license status
    async refreshLicenseStatus() {
        try {
            this.setLoading(true, 'Refreshing license status...');
            await this.fetchLicenseStatus();
            await this.fetchSubscriptionInfo();
            this.updateUI();
            this.showSuccess('License status refreshed');
        } catch (error) {
            console.error('Failed to refresh license status:', error);
            this.showError('Failed to refresh license status');
        } finally {
            this.setLoading(false);
        }
    },
    
    // Update UI based on current data
    updateUI() {
        this.updateLicenseStatus();
        this.updateSubscriptionInfo();
        this.updateFeatureAccess();
    },
    
    // Update license status display
    updateLicenseStatus() {
        const statusContainer = document.getElementById('license-status-container');
        if (!statusContainer) return;
        
        const license = this.currentLicense;
        if (!license) return;
        
        // Update status badge
        const statusBadge = document.getElementById('license-status-badge');
        if (statusBadge) {
            statusBadge.className = `status-badge ${license.status}`;
            statusBadge.textContent = this.getStatusLabel(license.status);
        }
        
        // Update details
        const userEmail = document.getElementById('license-user-email');
        if (userEmail) {
            userEmail.textContent = license.user_email || 'N/A';
        }
        
        const userName = document.getElementById('license-user-name');
        if (userName) {
            userName.textContent = license.user_name || 'N/A';
        }
        
        const expires = document.getElementById('license-expires');
        if (expires) {
            expires.textContent = license.expires ? this.formatDate(license.expires) : 'N/A';
        }
        
        const daysRemaining = document.getElementById('license-days-remaining');
        if (daysRemaining) {
            if (license.days_remaining !== null) {
                daysRemaining.textContent = `${license.days_remaining} days`;
                daysRemaining.className = license.days_remaining <= 7 ? 'days-warning' : 'days-normal';
            } else {
                daysRemaining.textContent = 'N/A';
            }
        }
        
        const licenseType = document.getElementById('license-type');
        if (licenseType) {
            licenseType.textContent = license.license_type || 'N/A';
            licenseType.className = `license-type ${license.license_type}`;
        }
        
        // Show/hide deactivate button
        const deactivateBtn = document.getElementById('deactivate-license-btn');
        if (deactivateBtn) {
            deactivateBtn.style.display = license.status === 'active' ? 'block' : 'none';
        }
    },
    
    // Update subscription information display
    updateSubscriptionInfo() {
        const subscriptionContainer = document.getElementById('subscription-container');
        if (!subscriptionContainer || !this.subscriptionInfo) return;
        
        const sub = this.subscriptionInfo;
        
        // Update feature list
        const featureList = document.getElementById('feature-list');
        if (featureList) {
            featureList.innerHTML = '';
            
            Object.entries(sub.feature_details || {}).forEach(([key, feature]) => {
                const featureElement = document.createElement('div');
                featureElement.className = `feature-item ${feature.enabled ? 'enabled' : 'disabled'}`;
                featureElement.innerHTML = `
                    <div class="feature-icon">${feature.enabled ? '✅' : '❌'}</div>
                    <div class="feature-info">
                        <div class="feature-name">${feature.name}</div>
                        <div class="feature-description">${feature.description}</div>
                    </div>
                `;
                featureList.appendChild(featureElement);
            });
        }
        
        // Update trial status
        const trialStatus = document.getElementById('trial-status');
        if (trialStatus) {
            if (sub.is_trial) {
                trialStatus.textContent = 'Trial License';
                trialStatus.className = 'trial-badge active';
            } else {
                trialStatus.textContent = 'Full License';
                trialStatus.className = 'trial-badge full';
            }
        }
        
        // Show/hide trial generation
        const trialSection = document.getElementById('trial-generation-section');
        if (trialSection) {
            trialSection.style.display = sub.can_generate_trial ? 'block' : 'none';
        }
    },
    
    // Update feature access indicators
    updateFeatureAccess() {
        if (!this.subscriptionInfo) return;
        
        const features = this.subscriptionInfo.features || [];
        
        // Update feature badges throughout the UI
        document.querySelectorAll('[data-feature]').forEach(element => {
            const requiredFeature = element.dataset.feature;
            const hasFeature = features.includes(requiredFeature);
            
            element.classList.toggle('feature-enabled', hasFeature);
            element.classList.toggle('feature-disabled', !hasFeature);
            
            // Add lock icon for disabled features
            if (!hasFeature && !element.querySelector('.feature-lock')) {
                const lockIcon = document.createElement('span');
                lockIcon.className = 'feature-lock';
                lockIcon.innerHTML = '🔒';
                element.appendChild(lockIcon);
            }
        });
    },
    
    // Handle WebSocket messages
    handleWebSocketMessage(message) {
        if (!message.type) return;
        
        switch (message.type) {
            case 'license_status_updated':
                console.log('📡 License status updated via WebSocket');
                this.currentLicense = message.data;
                this.updateLicenseStatus();
                break;
                
            case 'license_activation_started':
                window.APEX.addTerminalLine('License', message.data.message, 'info');
                break;
                
            case 'license_activation_success':
                window.APEX.addTerminalLine('License', message.data.message, 'success');
                this.showSuccess('License activated successfully!');
                setTimeout(() => this.refreshLicenseStatus(), 1000);
                break;
                
            case 'license_activation_failed':
                window.APEX.addTerminalLine('License', message.data.message, 'error');
                this.showError(message.data.error || 'License activation failed');
                break;
                
            case 'trial_generation_started':
                window.APEX.addTerminalLine('License', message.data.message, 'info');
                break;
                
            case 'trial_generation_success':
                window.APEX.addTerminalLine('License', message.data.message, 'success');
                window.APEX.addTerminalLine('License', `🔑 License Key: ${message.data.license_key}`, 'license-key');
                this.showGeneratedLicenseKey(message.data.license_key);
                break;
                
            case 'trial_generation_failed':
                window.APEX.addTerminalLine('License', message.data.message, 'error');
                this.showError(message.data.error || 'Trial generation failed');
                break;
                
            case 'license_deactivation_started':
                window.APEX.addTerminalLine('License', message.data.message, 'info');
                break;
                
            case 'license_deactivation_success':
                window.APEX.addTerminalLine('License', message.data.message, 'success');
                this.showSuccess('License deactivated successfully');
                setTimeout(() => this.refreshLicenseStatus(), 1000);
                break;
                
            case 'license_deactivation_failed':
                window.APEX.addTerminalLine('License', message.data.message, 'error');
                this.showError(message.data.error || 'License deactivation failed');
                break;
        }
    },
    
    // Show generated license key in a modal or special display
    showGeneratedLicenseKey(licenseKey) {
        // Create modal for license key display
        const modal = document.createElement('div');
        modal.className = 'license-key-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>🎉 Trial License Generated!</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Your trial license key has been generated:</p>
                    <div class="license-key-display">
                        <code>${licenseKey}</code>
                        <button class="copy-btn" data-license-key="${licenseKey}">📋 Copy</button>
                    </div>
                    <p class="modal-note">Save this key in a secure location. You can use it to activate APEX on any device.</p>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary activate-now-btn" data-license-key="${licenseKey}">Activate Now</button>
                    <button class="btn-secondary modal-close">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Bind modal events
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.querySelector('.copy-btn').addEventListener('click', () => {
            this.copyLicenseKey({target: modal.querySelector('.copy-btn')});
        });
        
        modal.querySelector('.activate-now-btn').addEventListener('click', () => {
            document.getElementById('license-key-input').value = licenseKey;
            modal.remove();
            // Switch to activation tab if exists
            const activationTab = document.querySelector('[data-tab="license-activation"]');
            if (activationTab) activationTab.click();
        });
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    },
    
    // Utility functions
    getStatusLabel(status) {
        const labels = {
            'active': '✅ Active',
            'inactive': '❌ Inactive',
            'invalid': '⚠️ Invalid',
            'expired': '⏰ Expired',
            'error': '🔴 Error'
        };
        return labels[status] || status;
    },
    
    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        } catch {
            return dateString;
        }
    },
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    setLoading(loading, message = '') {
        const loadingIndicator = document.getElementById('profile-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = loading ? 'block' : 'none';
            if (message) {
                loadingIndicator.textContent = message;
            }
        }
        
        // Disable form buttons during loading
        const buttons = document.querySelectorAll('#profile-tab button');
        buttons.forEach(btn => {
            btn.disabled = loading;
        });
    },
    
    showSuccess(message) {
        this.showToast(message, 'success');
    },
    
    showError(message) {
        this.showToast(message, 'error');
    },
    
    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
                <span class="toast-message">${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Show with animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('profile-tab')) {
        window.APEX.Profile.init();
    }
});

console.log('✅ APEX Profile component loaded');