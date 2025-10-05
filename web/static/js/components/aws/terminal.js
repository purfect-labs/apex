// AWS Terminal Component
class AWSTerminalComponent {
    constructor() {
        this.currentEnv = 'dev';
        this.render();
        this.bindEvents();
        this.listenForEnvironmentChanges();
    }

    render() {
        const container = document.getElementById('aws-terminal');
        if (!container) return;

        container.innerHTML = `
            <div class="command-category">
                <div class="category-title">🗄️ Database & Terminal</div>
                <div class="command-grid">
                    <button class="command-btn" data-action="connect-db">
                        <div class="command-icon">🚀</div>
                        <div><strong>Connect DB</strong></div>
                        <div class="command-desc">Connect via pre-built container</div>
                    </button>
                    <button class="command-btn" data-action="db-dev">
                        <div class="command-icon">🔵</div>
                        <div><strong>Dev DB</strong></div>
                        <div class="command-desc">Force dev environment</div>
                    </button>
                    <button class="command-btn" data-action="db-staging">
                        <div class="command-icon">🔶</div>
                        <div><strong>Staging DB</strong></div>
                        <div class="command-desc">Force staging environment</div>
                    </button>
                    <button class="command-btn" data-action="db-prod">
                        <div class="command-icon">🔴</div>
                        <div><strong>Prod DB</strong></div>
                        <div class="command-desc">Force production environment</div>
                    </button>
                    <button class="command-btn" data-action="check-port">
                        <div class="command-icon">🔍</div>
                        <div><strong>Check Port 5432</strong></div>
                        <div class="command-desc">Check PostgreSQL port</div>
                    </button>
                    <button class="command-btn" data-action="rds-instances">
                        <div class="command-icon">☁️</div>
                        <div><strong>RDS Instances</strong></div>
                        <div class="command-desc">List AWS RDS instances</div>
                    </button>
                </div>
            </div>
        `;
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('#aws-terminal .command-btn')) {
                const action = e.target.closest('.command-btn').dataset.action;
                this.handleAction(action);
            }
        });
    }

    listenForEnvironmentChanges() {
        window.addEventListener('environmentChanged', (e) => {
            this.currentEnv = e.detail.environment;
        });
    }

    handleAction(action) {
        switch (action) {
            case 'connect-db':
                this.connectDatabase();
                break;
            case 'db-dev':
                this.connectDatabase('dev');
                break;
            case 'db-staging':
                this.connectDatabase('staging');
                break;
            case 'db-prod':
                this.connectDatabase('prod');
                break;
            case 'check-port':
                this.checkPort();
                break;
            case 'rds-instances':
                this.listRDSInstances();
                break;
        }
    }

    connectDatabase(forceEnv = null) {
        const env = forceEnv || this.currentEnv;
        
        if (window.addTerminalLine) {
            window.addTerminalLine('AWS', `🗄️ Connecting to ${env} database...`, 'success');
            window.addTerminalLine('AWS', `🐳 Using pre-built container with SSM capability`, 'success');
        }

        // Send database connection request
        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            window.ws.send(JSON.stringify({
                type: 'database_connect',
                data: {
                    provider: 'aws',
                    env: env,
                    action: 'connect'
                }
            }));
        } else {
            // Fallback to API
            fetch('/api/database/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    provider: 'aws',
                    env: env
                })
            }).then(response => response.json())
              .then(data => {
                  if (window.addTerminalLine) {
                      window.addTerminalLine('AWS', `Database connection request sent: ${data.status}`, 'success');
                  }
              })
              .catch(error => {
                  if (window.addTerminalLine) {
                      window.addTerminalLine('AWS', `Error: ${error}`, 'error');
                  }
              });
        }
    }

    checkPort() {
        if (window.executeCommand) {
            window.executeCommand('lsof -i :5432');
        }
    }

    listRDSInstances() {
        if (window.executeCommand) {
            window.executeCommand(`aws rds describe-db-instances --profile ${this.currentEnv}`);
        }
    }
}

// Auto-initialize when loaded
window.AWSTerminalComponent = AWSTerminalComponent;