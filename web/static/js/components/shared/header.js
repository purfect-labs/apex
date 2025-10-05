// Shared Header Component
class HeaderComponent {
    constructor() {
        this.render();
        this.bindEvents();
    }

    render() {
        const headerElement = document.getElementById('header');
        if (!headerElement) return;

        headerElement.innerHTML = `
            <header class="ctl-header">
                <div class="ctl-title">
                    <span>⚡ CTL</span>
                    <span style="font-size: 0.8rem; color: var(--neon-blue); margin-left: 0.5rem;">COMMAND CENTER</span>
                </div>
                
                <div class="system-status">
                    <!-- Environment Toggles -->
                    <div class="status-item">
                        <div class="status-label">Environment</div>
                        <div class="env-toggles" style="display: flex; gap: 0.3rem;">
                            <button class="env-toggle active" data-env="dev">dev</button>
                            <button class="env-toggle" data-env="staging">staging</button>
                            <button class="env-toggle" data-env="prod">prod</button>
                        </div>
                    </div>
                    
                    <!-- AWS SSO Status -->
                    <div class="status-item">
                        <div class="status-label">AWS SSO</div>
                        <div class="status-value status-warning" id="sso-status" style="cursor: pointer;">checking...</div>
                    </div>
                    
                    <!-- Cloud Provider -->
                    <div class="status-item">
                        <div class="status-label">Cloud</div>
                        <div class="cloud-toggles" style="display: flex; gap: 0.3rem;">
                            <button class="cloud-toggle active" data-cloud="aws">AWS</button>
                            <button class="cloud-toggle" data-cloud="gcp">GCP</button>
                        </div>
                    </div>
                    
                    <!-- System Health -->
                    <div class="status-item">
                        <div class="status-label">Health</div>
                        <div class="status-value status-healthy" id="health-status">100%</div>
                    </div>
                </div>
            </header>
        `;
    }

    bindEvents() {
        // Environment switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('env-toggle')) {
                this.switchEnvironment(e.target.dataset.env);
            }
            if (e.target.classList.contains('cloud-toggle')) {
                this.switchCloud(e.target.dataset.cloud);
            }
            if (e.target.id === 'sso-status') {
                this.checkAWSSSO();
            }
        });
    }

    switchEnvironment(env) {
        // Update toggle buttons
        document.querySelectorAll('.env-toggle').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-env') === env) {
                btn.classList.add('active');
            }
        });
        
        // Broadcast environment change
        window.dispatchEvent(new CustomEvent('environmentChanged', { 
            detail: { environment: env } 
        }));
        
        // Update terminal
        if (window.addTerminalLine) {
            window.addTerminalLine('System', `Switching to ${env} environment...`, 'success');
        }
    }

    switchCloud(cloud) {
        // Update toggle buttons  
        document.querySelectorAll('.cloud-toggle').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-cloud') === cloud) {
                btn.classList.add('active');
            }
        });
        
        // Broadcast cloud change
        window.dispatchEvent(new CustomEvent('cloudChanged', { 
            detail: { cloud: cloud } 
        }));
        
        // Update terminal
        if (window.addTerminalLine) {
            window.addTerminalLine('System', `Switching to ${cloud.toUpperCase()}...`, 'success');
        }
    }

    checkAWSSSO() {
        const ssoStatus = document.getElementById('sso-status');
        ssoStatus.textContent = 'checking...';
        ssoStatus.className = 'status-value status-warning';
        
        if (window.addTerminalLine) {
            window.addTerminalLine('System', '🔐 Checking AWS SSO status...', 'success');
        }
        
        // Broadcast SSO check
        window.dispatchEvent(new CustomEvent('ssoCheckRequested'));
        
        // Simulate status check (would be replaced by actual API call)
        setTimeout(() => {
            const isLoggedIn = Math.random() > 0.5;
            if (isLoggedIn) {
                ssoStatus.textContent = 'logged in';
                ssoStatus.className = 'status-value status-healthy';
                if (window.addTerminalLine) {
                    window.addTerminalLine('System', '✅ AWS SSO: Logged in', 'success');
                }
            } else {
                ssoStatus.textContent = 'login required';
                ssoStatus.className = 'status-value status-error';
                if (window.addTerminalLine) {
                    window.addTerminalLine('System', '❌ AWS SSO: Login required', 'error');
                }
            }
        }, 2000);
    }

    getCurrentEnvironment() {
        const activeEnv = document.querySelector('.env-toggle.active');
        return activeEnv ? activeEnv.dataset.env : 'dev';
    }

    getCurrentCloud() {
        const activeCloud = document.querySelector('.cloud-toggle.active');
        return activeCloud ? activeCloud.dataset.cloud : 'aws';
    }
}

// Auto-initialize when loaded
window.HeaderComponent = HeaderComponent;