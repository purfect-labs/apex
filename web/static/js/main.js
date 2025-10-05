// APEX Main JavaScript Initialization

// Status checking functions (throttled)
let lastSSOCheck = 0;
let lastGCPCheck = 0;

async function checkAWSSSO() {
    const now = Date.now();
    
    // Throttle SSO checks to prevent spam (minimum 5 seconds between checks)
    if (now - lastSSOCheck < 5000) {
        console.log('Throttling AWS SSO status check');
        return;
    }
    lastSSOCheck = now;
    
    const ssoStatus = document.getElementById('sso-status');
    ssoStatus.textContent = 'checking...';
    ssoStatus.className = 'status-value status-warning';
    
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        // More flexible AWS authentication detection
        const awsAuthenticated = status.aws && (
            status.aws.authentication?.all_authenticated || 
            status.aws.authentication?.authenticated_profiles?.length > 0 ||
            (status.aws.authentication?.profiles && Object.values(status.aws.authentication.profiles).some(p => p.authenticated))
        );
        
        console.log('AWS Status Debug:', {
            hasAws: !!status.aws,
            hasAuth: !!status.aws?.authentication,
            allAuth: status.aws?.authentication?.all_authenticated,
            profiles: status.aws?.authentication?.profiles,
            awsAuthenticated
        });
        
        if (awsAuthenticated) {
            ssoStatus.textContent = 'logged in';
            ssoStatus.className = 'status-value status-healthy';
        } else {
            ssoStatus.textContent = 'login required';
            ssoStatus.className = 'status-value status-error';
        }
    } catch (error) {
        ssoStatus.textContent = 'error';
        ssoStatus.className = 'status-value status-error';
        console.error('AWS SSO status check failed:', error);
    }
}

async function checkGCPAuth() {
    const now = Date.now();
    
    // Throttle GCP checks to prevent spam (minimum 5 seconds between checks)
    if (now - lastGCPCheck < 5000) {
        console.log('Throttling GCP auth status check');
        return;
    }
    lastGCPCheck = now;
    
    const gcpStatus = document.getElementById('gcp-status');
    gcpStatus.textContent = 'checking...';
    gcpStatus.className = 'status-value status-warning';
    
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        // Check GCP authentication status
        const gcpAuthenticated = status.gcp && (
            status.gcp.authentication?.authenticated ||
            status.gcp.authentication?.active_account
        );
        
        console.log('GCP Status Debug:', {
            hasGcp: !!status.gcp,
            hasAuth: !!status.gcp?.authentication,
            authenticated: status.gcp?.authentication?.authenticated,
            activeAccount: status.gcp?.authentication?.active_account,
            gcpAuthenticated
        });
        
        if (gcpAuthenticated) {
            const account = status.gcp.authentication.active_account;
            gcpStatus.textContent = 'logged in';
            gcpStatus.className = 'status-value status-healthy';
            gcpStatus.title = `GCP: ${account}`;
        } else {
            gcpStatus.textContent = 'login required';
            gcpStatus.className = 'status-value status-error';
            gcpStatus.title = 'GCP authentication required';
        }
    } catch (error) {
        gcpStatus.textContent = 'error';
        gcpStatus.className = 'status-value status-error';
        console.error('GCP auth status check failed:', error);
    }
}

// Log functions
function clearLogs() {
    const output = document.getElementById('logs-output');
    if (output) {
        output.innerHTML = `
            <div class="terminal-line">
                <span class="terminal-prompt">📊</span>
                <span class="terminal-success">Logs cleared</span>
            </div>
        `;
    }
}

function toggleLogs() {
    const btn = document.getElementById('logs-toggle');
    if (btn) {
        if (btn.textContent === 'Pause') {
            btn.textContent = 'Resume';
            window.APEX.addTerminalLine('System', '⏸️ Log monitoring paused', 'warning');
        } else {
            btn.textContent = 'Pause';
            window.APEX.addTerminalLine('System', '▶️ Log monitoring resumed', 'success');
        }
    }
}

// Make functions available globally
window.checkAWSSSO = checkAWSSSO;
window.checkGCPAuth = checkGCPAuth;
window.clearLogs = clearLogs;
window.toggleLogs = toggleLogs;
window.updateStopButton = window.APEX.updateStopButton || function() {};

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 APEX Command Center initializing...');
    
    try {
        // Initialize all components
        window.APEX.initializeTabs();
        initializeCommandButtons();
        initializeTerminalInput();
        window.APEX.initWebSocket();
        
        // Show welcome message and check auth status once
        setTimeout(() => {
            window.APEX.addTerminalLine('System', '🚀 APEX Command Center ready!', 'success');
            window.APEX.addTerminalLine('System', '📡 WebSocket connection established', 'success');
            
            // Check both AWS and GCP status on startup
            checkAWSSSO();
            checkGCPAuth();
        }, 1000);
        
        console.log('✅ APEX Command Center initialized!');
    } catch (error) {
        console.error('Initialization error:', error);
        if (window.APEX && window.APEX.addTerminalLine) {
            window.APEX.addTerminalLine('Error', `Initialization failed: ${error}`, 'error');
        }
    }
});
