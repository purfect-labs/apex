// APEX Web UI Controller
class ApexWebUI {
    constructor() {
        this.socket = null;
        this.terminal = null;
        this.fitAddon = null;
        this.logs = [];
        this.config = null;
        
        this.init();
    }

    async init() {
        console.log('🚀 Initializing APEX Web UI...');
        
        // Check initial status
        await this.checkStatus();
        
        // Load config
        await this.loadConfig();
        
        // Initialize WebSocket connection
        this.initWebSocket();
        
        // Initialize terminal
        this.initTerminal();
        
        // Bind event listeners
        this.bindEvents();
        
        console.log('✅ APEX Web UI ready!');
    }

    async checkStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            this.updateConfigStatus(status.configReady);
            this.log(`Status check: Config ${status.configReady ? 'ready' : 'not ready'}`);
            
            // Also check AWS authentication status
            await this.checkAWSStatus();
            
            return status;
        } catch (error) {
            console.error('❌ Failed to check status:', error);
            this.updateConfigStatus(false, 'Failed to check configuration');
        }
    }
    
    async loadConfig() {
        try {
            const cloud = document.getElementById('cloud-select').value;
            const env = document.getElementById('env-select').value;
            
            const response = await fetch(`/api/config?cloud=${cloud}&env=${env}`);
            if (response.ok) {
                this.config = await response.json();
                this.updatePsqlCommand();
                this.log(`Config loaded for ${cloud}/${env}: ${this.config.db_name}@${this.config.db_host}`);
            } else {
                this.log('Failed to load config - using defaults');
            }
        } catch (error) {
            console.error('❌ Failed to load config:', error);
            this.log('Config loading error - using defaults');
        }
    }
    
    async checkAWSStatus() {
        const env = document.getElementById('env-select').value;
        try {
            const response = await fetch(`/api/aws-status?env=${env}`);
            const awsStatus = await response.json();
            
            this.updateAWSStatus(awsStatus);
            this.log(`AWS auth check for ${env}: ${awsStatus.authenticated ? 'authenticated' : 'not authenticated'}`);
        } catch (error) {
            console.error('❌ Failed to check AWS status:', error);
        }
    }
    
    updateAWSStatus(awsStatus) {
        const ssoStatus = document.getElementById('sso-status');
        if (awsStatus.authenticated) {
            // Smart verification - if we got STS response, we're authenticated
            const userName = awsStatus.identity?.Arn?.split('/').pop() || 'AWS User';
            this.showActionStatus('sso-status', 'success', `✅ Authenticated as ${userName}`);
        } else {
            this.showActionStatus('sso-status', 'error', '❌ Not authenticated - run preflight checks on host');
        }
    }
    
    updatePsqlCommand() {
        if (this.config) {
            const command = `psql -h 127.0.0.1 -p 15432 -U ${this.config.db_user} ${this.config.db_name}`;
            const cmdElement = document.getElementById('psql-command');
            if (cmdElement) {
                cmdElement.textContent = command;
            }
        }
    }

    updateConfigStatus(ready, errorMsg = null) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        statusDot.className = 'status-dot';
        
        if (errorMsg) {
            statusDot.classList.add('error');
            statusText.textContent = errorMsg;
        } else if (ready) {
            statusDot.classList.add('ready');
            statusText.textContent = 'Configuration ready';
        } else {
            statusText.textContent = 'Configuration incomplete - run build.sh first';
        }
    }

    initWebSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.log('🔗 Connected to server');
            this.socket.emit('create-terminal');
        });
        
        this.socket.on('disconnect', () => {
            this.log('💔 Disconnected from server');
        });
        
        this.socket.on('terminal-ready', () => {
            this.log('💻 Terminal session ready');
        });
        
        this.socket.on('terminal-output', (data) => {
            console.log('Received terminal output:', data.replace('\r', '\\r').replace('\n', '\\n'));
            if (this.terminal) {
                this.terminal.write(data);
                console.log('Wrote to terminal');
            } else {
                console.error('Terminal not available to write output');
            }
        });
        
        this.socket.on('terminal-exit', () => {
            this.log('🚪 Terminal session ended');
            // Reconnect terminal
            setTimeout(() => {
                this.socket.emit('create-terminal');
            }, 1000);
        });
        
        this.socket.on('terminal-error', (error) => {
            this.log('❌ Terminal error: ' + error);
            console.error('Terminal error:', error);
        });
    }

    initTerminal() {
        console.log('💻 Initializing terminal...');
        
        try {
            // Check if Terminal is available
            if (typeof Terminal === 'undefined') {
                console.error('Terminal class not loaded from xterm.js');
                return;
            }
            
            // Initialize xterm.js terminal
            this.terminal = new Terminal({
                theme: {
                    background: '#1e1e1e',
                    foreground: '#d4d4d4',
                    cursor: '#4fc3f7',
                    selection: '#3c3c3c'
                },
                fontFamily: 'SF Mono, Monaco, Consolas, Liberation Mono, Courier New, monospace',
                fontSize: 14,
                lineHeight: 1.2,
                cursorBlink: true,
                convertEol: true
            });
            console.log('Terminal created successfully');

            // Try to load fit addon
            if (typeof FitAddon !== 'undefined') {
                console.log('FitAddon available, loading...');
                this.fitAddon = new FitAddon.FitAddon();
                this.terminal.loadAddon(this.fitAddon);
                console.log('FitAddon loaded');
            } else {
                console.warn('FitAddon not available - terminal will not auto-resize');
            }
            
            // Open terminal in container
            const terminalContainer = document.getElementById('terminal');
            if (!terminalContainer) {
                console.error('Terminal container #terminal not found');
                return;
            }
            console.log('Terminal container found:', terminalContainer);
            
            this.terminal.open(terminalContainer);
            console.log('Terminal opened in container');
            
            // Fit terminal to container if addon is available
            if (this.fitAddon) {
                this.fitAddon.fit();
                console.log('Terminal fitted, cols:', this.terminal.cols, 'rows:', this.terminal.rows);
            } else {
                console.log('Terminal size: cols:', this.terminal.cols, 'rows:', this.terminal.rows);
            }
            
            // Handle terminal input
            this.terminal.onData((data) => {
                console.log('Terminal input:', data.replace('\r', '\\r').replace('\n', '\\n'));
                if (this.socket) {
                    this.socket.emit('terminal-input', data);
                } else {
                    console.error('Socket not available for terminal input');
                }
            });
            
            // Handle window resize
            if (this.fitAddon) {
                window.addEventListener('resize', () => {
                    this.fitAddon.fit();
                    if (this.socket) {
                        this.socket.emit('terminal-resize', {
                            cols: this.terminal.cols,
                            rows: this.terminal.rows
                        });
                    }
                });
            }
            
            // Focus the terminal to ensure it can receive input
            setTimeout(() => {
                this.terminal.focus();
                console.log('Terminal focused');
            }, 1000);
            
            this.log('💻 Terminal initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize terminal:', error);
            this.log('❌ Terminal initialization failed: ' + error.message);
        }
    }

    bindEvents() {
        // SSO Auth button
        const ssoBtn = document.getElementById('sso-auth-btn');
        ssoBtn.addEventListener('click', () => this.runSSOAuth());
        
        // DB Connect button
        const dbBtn = document.getElementById('db-connect-btn');
        dbBtn.addEventListener('click', () => this.runDBConnect());
        
        // PSQL Connect button
        const psqlBtn = document.getElementById('psql-connect-btn');
        psqlBtn.addEventListener('click', () => this.connectPsqlInTerminal());
        
        // Quick PSQL button
        const quickPsqlBtn = document.getElementById('quick-psql-btn');
        quickPsqlBtn.addEventListener('click', () => this.connectPsqlInTerminal());
        
        // AWS Identity button
        const identityBtn = document.getElementById('aws-identity-btn');
        identityBtn.addEventListener('click', () => this.verifyAWSIdentity());
        
        // Environment selector change
        document.getElementById('env-select').addEventListener('change', () => {
            this.checkAWSStatus();
            this.loadConfig(); // Reload config when environment changes
        });
        
        // Cloud selector change
        document.getElementById('cloud-select').addEventListener('change', () => {
            this.checkAWSStatus();
            this.loadConfig(); // Reload config when cloud changes
        });
        
        // Terminal controls
        document.getElementById('terminal-clear').addEventListener('click', () => {
            this.terminal.clear();
        });
        
        document.getElementById('terminal-reset').addEventListener('click', () => {
            if (this.socket) {
                this.socket.emit('create-terminal');
            }
        });
    }

    async runSSOAuth() {
        const cloud = document.getElementById('cloud-select').value;
        const env = document.getElementById('env-select').value;
        
        this.log(`🔐 Checking SSO authentication for ${cloud}/${env}...`);
        this.showActionStatus('sso-status', 'loading', 'Checking authentication...');
        
        const btn = document.getElementById('sso-auth-btn');
        btn.disabled = true;
        
        try {
            // Check current AWS status first
            const response = await fetch(`/api/aws-status?env=${env}`);
            const awsStatus = await response.json();
            
            if (awsStatus.authenticated) {
                // If we can get STS identity, authentication is working!
                const userName = awsStatus.identity?.Arn?.split('/').pop() || 'AWS User';
                this.showActionStatus('sso-status', 'success', `✅ Already authenticated as ${userName}`);
                this.log(`✅ SSO check passed for ${env}: ${userName}`);
            } else {
                // Show instructions for host-side authentication
                this.showActionStatus('sso-status', 'error', 
                    `💻 SSO must be done on HOST. Run: APEX_ENV=${env} APEX_CLOUD=${cloud} bin/aws-sso-auth.sh`);
                
                // Show in terminal
                if (this.terminal) {
                    this.terminal.writeln('\r\n--- SSO Authentication Required ---');
                    this.terminal.writeln(`Run this command on your host (macOS):`);
                    this.terminal.writeln(`APEX_ENV=${env} APEX_CLOUD=${cloud} bin/aws-sso-auth.sh`);
                    this.terminal.writeln('Then refresh this page or restart the container.');
                    this.terminal.writeln('--- End Instructions ---\r\n');
                }
            }
            
        } catch (error) {
            this.log(`❌ SSO auth check error: ${error.message}`);
            this.showActionStatus('sso-status', 'error', `Network error: ${error.message}`);
        } finally {
            btn.disabled = false;
        }
    }

    async runDBConnect() {
        const cloud = document.getElementById('cloud-select').value;
        const env = document.getElementById('env-select').value;
        
        this.log(`🔗 Starting database connection for ${cloud}/${env}...`);
        this.showActionStatus('db-status', 'loading', 'Setting up database connection...');
        
        const btn = document.getElementById('db-connect-btn');
        btn.disabled = true;
        
        try {
            const response = await fetch('/api/run-db-connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cloud, env })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.log('✅ Database connection started in background');
                this.showActionStatus('db-status', 'success', 'Database tunnel active! Use psql -h 127.0.0.1 -p 15432');
            } else {
                this.log('❌ Database connection failed');
                this.showActionStatus('db-status', 'error', `Connection failed: ${result.error}`);
            }
            
            // Show output in terminal if available
            if (result.output && this.terminal) {
                this.terminal.writeln('\r\n--- DB Connect Output ---');
                this.terminal.writeln(result.output);
                this.terminal.writeln('--- End Output ---\r\n');
            }
            
        } catch (error) {
            this.log(`❌ DB connect error: ${error.message}`);
            this.showActionStatus('db-status', 'error', `Network error: ${error.message}`);
        } finally {
            btn.disabled = false;
        }
    }
    
    connectPsqlInTerminal() {
        if (this.config && this.terminal) {
            const command = `psql -h 127.0.0.1 -p 15432 -U ${this.config.db_user} ${this.config.db_name}`;
            this.terminal.write(command + '\r');
            if (this.socket) {
                this.socket.emit('terminal-input', command + '\r');
            }
            this.log(`Sent psql command to terminal: ${command}`);
        } else {
            this.log('❌ Config not loaded or terminal not ready');
        }
    }
    
    async verifyAWSIdentity() {
        const env = document.getElementById('env-select').value;
        const btn = document.getElementById('aws-identity-btn');
        
        btn.disabled = true;
        this.showActionStatus('identity-status', 'loading', 'Verifying AWS identity...');
        
        try {
            const response = await fetch(`/api/aws-status?env=${env}`);
            const awsStatus = await response.json();
            
            if (awsStatus.authenticated) {
                const userName = awsStatus.identity?.Arn?.split('/').pop() || 'Unknown';
                const accountId = awsStatus.identity?.Account || 'Unknown';
                this.showActionStatus('identity-status', 'success', 
                    `✅ Identity verified: ${userName} (Account: ${accountId})`);
                this.log(`✅ AWS identity verified for ${env}: ${userName}`);
                
                // Also send to terminal
                if (this.terminal) {
                    this.terminal.writeln('\r\n--- AWS Identity Verification ---');
                    this.terminal.writeln(`✅ Profile: ${env}`);
                    this.terminal.writeln(`✅ User: ${userName}`);
                    this.terminal.writeln(`✅ Account: ${accountId}`);
                    this.terminal.writeln('--- End Verification ---\r\n');
                }
            } else {
                this.showActionStatus('identity-status', 'error', 
                    '❌ Not authenticated - run aws sso login or check credentials');
                this.log(`❌ AWS identity verification failed for ${env}`);
                
                // Send command to terminal
                if (this.terminal) {
                    const command = `aws sts get-caller-identity --profile ${env}`;
                    this.terminal.write(command + '\r');
                    if (this.socket) {
                        this.socket.emit('terminal-input', command + '\r');
                    }
                }
            }
        } catch (error) {
            this.showActionStatus('identity-status', 'error', `Network error: ${error.message}`);
            this.log(`❌ Identity verification error: ${error.message}`);
        } finally {
            btn.disabled = false;
        }
    }

    showActionStatus(statusId, type, message) {
        const statusEl = document.getElementById(statusId);
        statusEl.className = `action-status show ${type}`;
        statusEl.textContent = message;
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                statusEl.classList.remove('show');
            }, 5000);
        }
    }

    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logMessage = `[${timestamp}] ${message}`;
        this.logs.push(logMessage);
        console.log(logMessage);
        
        // Keep only last 100 log entries
        if (this.logs.length > 100) {
            this.logs.shift();
        }
    }
}

// Global functions for HTML onclick handlers
function sendToTerminal(command) {
    if (window.apexUI && window.apexUI.terminal) {
        window.apexUI.terminal.write(command + '\r');
        if (window.apexUI.socket) {
            window.apexUI.socket.emit('terminal-input', command + '\r');
        }
    }
}

function toggleLogs() {
    const modal = document.getElementById('logs-modal');
    const isVisible = modal.style.display !== 'none';
    
    if (isVisible) {
        modal.style.display = 'none';
    } else {
        // Update logs content
        const logsContent = document.getElementById('logs-content');
        logsContent.textContent = window.apexUI ? window.apexUI.logs.join('\n') : 'No logs available';
        modal.style.display = 'flex';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.apexUI = new ApexWebUI();
});