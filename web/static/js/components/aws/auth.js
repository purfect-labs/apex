// AWS Auth Component
class AWSAuthComponent {
    constructor() {
        this.currentEnv = 'dev';
        this.render();
        this.bindEvents();
        this.listenForEnvironmentChanges();
    }

    render() {
        const container = document.getElementById('aws-auth');
        if (!container) return;

        container.innerHTML = `
            <div class="command-category">
                <div class="category-title">🔐 AWS SSO & Auth</div>
                <div class="command-grid">
                    <button class="command-btn" data-action="sso-login">
                        <div class="command-icon">🔑</div>
                        <div><strong>SSO Login</strong></div>
                        <div class="command-desc">AWS SSO auth (current env)</div>
                    </button>
                    <button class="command-btn" data-action="check-identity">
                        <div class="command-icon">👤</div>
                        <div><strong>Check Identity</strong></div>
                        <div class="command-desc">aws sts get-caller-identity</div>
                    </button>
                    <button class="command-btn" data-action="auth-all">
                        <div class="command-icon">🔄</div>
                        <div><strong>Auth All Profiles</strong></div>
                        <div class="command-desc">Login to dev/stage/prod</div>
                    </button>
                    <button class="command-btn" data-action="show-config">
                        <div class="command-icon">⚙️</div>
                        <div><strong>AWS Config</strong></div>
                        <div class="command-desc">Show AWS configuration</div>
                    </button>
                </div>
            </div>
        `;
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('#aws-auth .command-btn')) {
                const action = e.target.closest('.command-btn').dataset.action;
                this.handleAction(action);
            }
        });
    }

    listenForEnvironmentChanges() {
        window.addEventListener('environmentChanged', (e) => {
            this.currentEnv = e.detail.environment;
            this.updateEnvironmentDisplay();
        });
    }

    updateEnvironmentDisplay() {
        // Update any environment-specific displays in the component
        const desc = document.querySelector('#aws-auth .command-btn[data-action="sso-login"] .command-desc');
        if (desc) {
            desc.textContent = `AWS SSO auth (${this.currentEnv})`;
        }
    }

    handleAction(action) {
        switch (action) {
            case 'sso-login':
                this.ssoLogin();
                break;
            case 'check-identity':
                this.checkIdentity();
                break;
            case 'auth-all':
                this.authAllProfiles();
                break;
            case 'show-config':
                this.showConfig();
                break;
        }
    }

    ssoLogin() {
        if (window.addTerminalLine) {
            window.addTerminalLine('AWS', `🔐 Starting SSO login for ${this.currentEnv}...`, 'success');
        }

        // Send auth request via WebSocket or API
        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            window.ws.send(JSON.stringify({
                type: 'auth_request',
                data: {
                    provider: 'aws',
                    profile: this.currentEnv
                }
            }));
        } else {
            // Fallback to API
            fetch('/api/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    provider: 'aws',
                    profile: this.currentEnv,
                    env: this.currentEnv
                })
            }).then(response => response.json())
              .then(data => {
                  if (window.addTerminalLine) {
                      window.addTerminalLine('AWS', `SSO auth request sent: ${data.status}`, 'success');
                  }
              })
              .catch(error => {
                  if (window.addTerminalLine) {
                      window.addTerminalLine('AWS', `Error: ${error}`, 'error');
                  }
              });
        }
    }

    checkIdentity() {
        if (window.executeCommand) {
            window.executeCommand(`aws sts get-caller-identity --profile ${this.currentEnv}`);
        }
    }

    authAllProfiles() {
        if (window.addTerminalLine) {
            window.addTerminalLine('AWS', '🔄 Starting authentication for all profiles...', 'success');
        }

        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            window.ws.send(JSON.stringify({
                type: 'auth_request',
                data: {
                    provider: 'aws',
                    action: 'auth_all'
                }
            }));
        } else {
            fetch('/api/auth/aws/all', {
                method: 'POST'
            }).then(response => response.json())
              .then(data => {
                  if (window.addTerminalLine) {
                      window.addTerminalLine('AWS', `Auth all request sent: ${data.status}`, 'success');
                  }
              });
        }
    }

    showConfig() {
        if (window.executeCommand) {
            window.executeCommand('aws configure list');
        }
    }
}

// Auto-initialize when loaded
window.AWSAuthComponent = AWSAuthComponent;