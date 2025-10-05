# UI Layer Documentation

## 🎨 JavaScript, Templates, State Management & API Coherence

The UI layer provides real-time web interface with WebSocket communication, state management, and seamless API integration.

## 📁 Current Structure

```
apex/web/static/
├── css/
│   └── main.css           # Cyberpunk-themed styling
├── js/
│   ├── main.js            # Application initialization
│   └── components/
│       ├── shared/
│       │   ├── core.js    # WebSocket, terminal, global state
│       │   ├── tabs.js    # Tab component system
│       │   └── commands.js # Command execution framework
│       └── gcp/
│           └── kali.js    # Kiali-specific functionality
├── templates/
│   └── apex_compact.html # Main UI template
```

**Full Paths (from project root):**
- `apex/web/static/css/main.css`
- `apex/web/static/js/main.js`
- `apex/web/static/js/components/shared/core.js`
- `apex/web/static/js/components/shared/tabs.js`
- `apex/web/static/js/components/shared/commands.js`
- `apex/web/static/js/components/gcp/kali.js`
- `apex/web/templates/apex_compact.html`

## 🔄 State Management Architecture

### Global State Pattern (`apex/web/static/js/components/shared/core.js`)

```javascript
// File: apex/web/static/js/components/shared/core.js
// Global state management with encapsulation
window.APEX = {
    // State variables
    state: {
        isExecuting: false,
        commandHistory: [],
        currentEnvironment: 'dev',
        authStatus: {
            aws: { dev: false, stage: false, prod: false },
            gcp: { dev: false, stage: false, prod: false },
            k8s: { dev: false, stage: false, prod: false }
        },
        wsConnected: false,
        clientId: Math.random().toString(36).substr(2, 9)
    },
    
    // WebSocket management
    ws: null,
    wsReconnectAttempts: 0,
    wsMaxReconnectAttempts: 5,
    
    // Core functions
    initWebSocket,
    addTerminalLine,
    clearTerminal,
    stopCommand,
    updateCommandHistory,
    
    // State management functions
    setState: (key, value) => {
        APEX.state[key] = value;
        APEX.onStateChange(key, value);
    },
    
    getState: (key) => APEX.state[key],
    
    onStateChange: (key, value) => {
        // Update UI based on state changes
        if (key === 'isExecuting') {
            updateStopButton();
            updateExecutionState();
        } else if (key === 'currentEnvironment') {
            updateEnvironmentUI();
        } else if (key === 'authStatus') {
            updateAuthStatusUI();
        }
    }
};
```

### Environment State Management

```javascript
// File: apex/web/static/js/components/shared/core.js
function setCurrentEnvironment(env) {
    if (!['dev', 'stage', 'prod'].includes(env)) {
        console.error('Invalid environment:', env);
        return;
    }
    
    APEX.setState('currentEnvironment', env);
    
    // Update UI indicators
    document.querySelectorAll('.env-indicator').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.env === env) {
            el.classList.add('active');
        }
    });
    
    // Broadcast environment change to server
    if (APEX.ws && APEX.ws.readyState === WebSocket.OPEN) {
        APEX.ws.send(JSON.stringify({
            type: 'environment_change',
            data: { environment: env }
        }));
    }
}

function getCurrentEnvironment() {
    return APEX.getState('currentEnvironment');
}
```

### Authentication State Management

```javascript
// File: apex/web/static/js/components/shared/core.js
function updateAuthStatus(provider, env, status) {
    const currentAuth = APEX.getState('authStatus');
    if (!currentAuth[provider]) {
        currentAuth[provider] = {};
    }
    currentAuth[provider][env] = status;
    
    APEX.setState('authStatus', currentAuth);
    
    // Update status cards in UI
    const statusCard = document.getElementById(`${provider}-${env}-status`);
    if (statusCard) {
        statusCard.className = `status-card ${status ? 'status-healthy' : 'status-unhealthy'}`;
        statusCard.textContent = status ? '✅ Authenticated' : '❌ Not Authenticated';
    }
}

function getAuthStatus(provider, env) {
    const authStatus = APEX.getState('authStatus');
    return authStatus[provider] && authStatus[provider][env];
}
```

## 🌐 WebSocket Integration & Real-time Updates

### WebSocket Connection Management (`apex/web/static/js/components/shared/core.js`)

```javascript
// File: apex/web/static/js/components/shared/core.js
function initWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws/${APEX.getState('clientId')}`;
    APEX.ws = new WebSocket(wsUrl);
    
    APEX.ws.onopen = function(event) {
        console.log('🔗 WebSocket connected');
        APEX.setState('wsConnected', true);
        APEX.wsReconnectAttempts = 0;
        
        // Show connection status
        const statusIndicator = document.getElementById('ws-status');
        if (statusIndicator) {
            statusIndicator.className = 'ws-connected';
            statusIndicator.textContent = '🟢 Connected';
        }
    };
    
    APEX.ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
    
    APEX.ws.onclose = function(event) {
        console.log('❌ WebSocket disconnected');
        APEX.setState('wsConnected', false);
        
        // Show disconnection status
        const statusIndicator = document.getElementById('ws-status');
        if (statusIndicator) {
            statusIndicator.className = 'ws-disconnected';
            statusIndicator.textContent = '🔴 Disconnected';
        }
        
        // Attempt reconnection
        if (APEX.wsReconnectAttempts < APEX.wsMaxReconnectAttempts) {
            setTimeout(() => {
                APEX.wsReconnectAttempts++;
                console.log(`🔄 Reconnecting WebSocket (attempt ${APEX.wsReconnectAttempts})`);
                initWebSocket();
            }, 2000 * APEX.wsReconnectAttempts);
        }
    };
}

function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'command_output':
            addTerminalLine('Output', message.data.output, 'success');
            break;
            
        case 'aws_auth_started':
            addTerminalLine('AWS Auth', `🔐 ${message.data.message}`, 'info');
            break;
            
        case 'aws_auth_success':
            addTerminalLine('AWS Auth', `✅ ${message.data.message}`, 'success');
            updateAuthStatus('aws', message.data.profile, true);
            break;
            
        case 'gcp_auth_success':
            addTerminalLine('GCP Auth', `✅ ${message.data.message}`, 'success');
            updateAuthStatus('gcp', 'dev', true);
            break;
            
        case 'context_switch_failure':
            addTerminalLine('Error', `❌ ${message.data.message}`, 'error');
            showContextFailureModal(message.data);
            break;
            
        case 'command_started':
            APEX.setState('isExecuting', true);
            addTerminalLine('System', `⚡ ${message.data.command}`, 'command');
            break;
            
        case 'command_completed':
            APEX.setState('isExecuting', false);
            const status = message.data.success ? 'success' : 'error';
            addTerminalLine('System', `${message.data.success ? '✅' : '❌'} Command completed`, status);
            break;
            
        default:
            console.log('Unknown WebSocket message type:', message.type);
    }
}
```

## 🎯 API Coherence Patterns

### Command Execution API Integration

```javascript
// File: apex/web/static/js/components/shared/commands.js
class CommandExecutor {
    static async executeProviderCommand(provider, action, params = {}) {
        const currentEnv = getCurrentEnvironment();
        
        const requestData = {
            provider: provider,
            action: action,
            environment: currentEnv,
            ...params
        };
        
        try {
            // Show command started in UI
            addTerminalLine('System', `🚀 Executing ${provider} ${action} (${currentEnv})`, 'info');
            
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (!result.success) {
                addTerminalLine('Error', `❌ ${result.error}`, 'error');
                return false;
            }
            
            // Command started successfully - real-time output will come via WebSocket
            return true;
            
        } catch (error) {
            addTerminalLine('Error', `❌ Network error: ${error.message}`, 'error');
            return false;
        }
    }
    
    static async executeDirectCommand(endpoint, data = {}) {
        const currentEnv = getCurrentEnvironment();
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    environment: currentEnv,
                    ...data
                })
            });
            
            return await response.json();
            
        } catch (error) {
            addTerminalLine('Error', `❌ API error: ${error.message}`, 'error');
            return { success: false, error: error.message };
        }
    }
}
```

### Provider-Specific API Integration

```javascript
// File: apex/web/static/js/components/shared/commands.js
// AWS API Integration
const AWSCommands = {
    async authenticate(profile = null) {
        const env = profile || getCurrentEnvironment();
        return await CommandExecutor.executeDirectCommand('/api/aws/auth', { 
            profile: env 
        });
    },
    
    async getStatus() {
        const response = await fetch('/api/aws/status');
        const result = await response.json();
        
        // Update UI with status information
        if (result.profiles) {
            Object.entries(result.profiles).forEach(([profile, status]) => {
                updateAuthStatus('aws', profile, status.authenticated);
            });
        }
        
        return result;
    },
    
    async executeCommand(command) {
        return await CommandExecutor.executeDirectCommand('/api/aws/execute', {
            command: command
        });
    }
};

// GCP API Integration  
const GCPCommands = {
    async authenticate() {
        return await CommandExecutor.executeProviderCommand('gcp', 'authenticate');
    },
    
    async connectKiali(environments = ['dev']) {
        const results = [];
        for (const env of environments) {
            const result = await CommandExecutor.executeDirectCommand(`/api/gcp/kali/forward/${env}`);
            results.push(result);
        }
        return results;
    }
};
```

## 🎨 Template Structure & Component Integration

### Main Template (`apex/web/templates/apex_compact.html`)

```html
<!-- File: apex/web/templates/apex_compact.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX Command Center</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="admin-container">
        <!-- Environment Selector -->
        <div class="environment-selector">
            <button class="env-btn" data-env="dev" onclick="setCurrentEnvironment('dev')">
                Dev
            </button>
            <button class="env-btn" data-env="stage" onclick="setCurrentEnvironment('stage')">
                Stage  
            </button>
            <button class="env-btn" data-env="prod" onclick="setCurrentEnvironment('prod')">
                Prod
            </button>
        </div>
        
        <!-- Connection Status -->
        <div class="status-bar">
            <span id="ws-status" class="ws-disconnected">🔴 Disconnected</span>
            <span id="current-env">Environment: <span id="env-display">dev</span></span>
        </div>
        
        <!-- Provider Status Cards -->
        <div class="provider-status">
            <!-- AWS Status -->
            <div class="provider-section" id="aws-provider">
                <h3>AWS Provider</h3>
                <div class="status-grid">
                    <div id="aws-dev-status" class="status-card">AWS Dev</div>
                    <div id="aws-stage-status" class="status-card">AWS Stage</div>
                    <div id="aws-prod-status" class="status-card">AWS Prod</div>
                </div>
                <div class="capability-buttons">
                    <button onclick="AWSCommands.authenticate()">Authenticate</button>
                    <button onclick="AWSCommands.getStatus()">Check Status</button>
                </div>
            </div>
            
            <!-- GCP Status -->  
            <div class="provider-section" id="gcp-provider">
                <h3>GCP Provider</h3>
                <div class="status-grid">
                    <div id="gcp-dev-status" class="status-card">GCP Dev</div>
                    <div id="gcp-stage-status" class="status-card">GCP Stage</div>
                    <div id="gcp-prod-status" class="status-card">GCP Prod</div>
                </div>
                <div class="capability-buttons">
                    <button onclick="GCPCommands.authenticate()">Authenticate</button>
                    <button onclick="GCPCommands.connectKiali(['dev'])">Connect Kiali</button>
                </div>
            </div>
        </div>
        
        <!-- Terminal Output -->
        <div class="terminal-section">
            <div class="terminal-header">
                <span>Command Output</span>
                <button onclick="clearTerminal()">Clear</button>
                <button id="stop-command" onclick="stopCommand()" disabled>Stop</button>
            </div>
            <div id="terminal-output" class="terminal-output"></div>
        </div>
        
        <!-- Command Input -->
        <div class="command-input-section">
            <input type="text" id="manual-command" placeholder="Enter command..." />
            <button onclick="executeManualCommand()">Execute</button>
        </div>
    </div>
    
    <!-- Load JavaScript -->
    <script src="/static/js/components/shared/core.js"></script>
    <script src="/static/js/components/shared/tabs.js"></script>
    <script src="/static/js/components/shared/commands.js"></script>
    <script src="/static/js/components/gcp/kali.js"></script>
    <script src="/static/js/main.js"></script>
</body>
</html>
```

### Component Initialization (`apex/web/static/js/main.js`)

```javascript
// File: apex/web/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 APEX UI Initializing...');
    
    // Initialize WebSocket connection
    initWebSocket();
    
    // Set default environment
    setCurrentEnvironment('dev');
    
    // Load provider statuses
    loadProviderStatuses();
    
    // Setup UI event listeners
    setupUIEventListeners();
    
    console.log('✅ APEX UI Ready');
});

async function loadProviderStatuses() {
    try {
        // Load AWS status
        const awsStatus = await AWSCommands.getStatus();
        console.log('AWS Status loaded:', awsStatus);
        
        // Load GCP status (when available)
        // const gcpStatus = await GCPCommands.getStatus();
        
    } catch (error) {
        console.error('Error loading provider statuses:', error);
    }
}

function setupUIEventListeners() {
    // Environment selector buttons
    document.querySelectorAll('.env-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const env = e.target.dataset.env;
            setCurrentEnvironment(env);
        });
    });
    
    // Manual command input
    const commandInput = document.getElementById('manual-command');
    if (commandInput) {
        commandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                executeManualCommand();
            }
        });
    }
}

async function executeManualCommand() {
    const input = document.getElementById('manual-command');
    const command = input.value.trim();
    
    if (!command) return;
    
    // Determine provider based on command
    if (command.startsWith('aws ')) {
        await AWSCommands.executeCommand(command.substring(4));
    } else if (command.startsWith('gcloud ')) {
        await CommandExecutor.executeProviderCommand('gcp', 'execute', { 
            command: command.substring(7) 
        });
    } else if (command.startsWith('kubectl ')) {
        await CommandExecutor.executeProviderCommand('k8s', 'execute', { 
            command: command.substring(8) 
        });
    } else {
        addTerminalLine('System', '❌ Unknown command prefix. Use: aws, gcloud, or kubectl', 'error');
    }
    
    // Clear input
    input.value = '';
}
```

## 🎨 CSS Styling System (`apex/web/static/css/main.css`)

```css
/* File: apex/web/static/css/main.css */
/* Cyberpunk-themed styling with real-time status indicators */

:root {
    --bg-primary: #0f0f0f;
    --bg-secondary: #1a1a1a;
    --accent-cyan: #00ffff;
    --accent-green: #00ff00;
    --accent-red: #ff0040;
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
}

body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Fira Code', monospace;
    margin: 0;
    padding: 0;
}

.admin-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* Environment Selector */
.environment-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.env-btn {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--accent-cyan);
    padding: 10px 20px;
    cursor: pointer;
    transition: all 0.3s;
}

.env-btn:hover {
    background: var(--accent-cyan);
    color: var(--bg-primary);
}

.env-btn.active {
    background: var(--accent-cyan);
    color: var(--bg-primary);
    box-shadow: 0 0 10px var(--accent-cyan);
}

/* Status Cards */
.status-card {
    background: var(--bg-secondary);
    border: 1px solid #333;
    padding: 15px;
    text-align: center;
    transition: all 0.3s;
}

.status-card.status-healthy {
    border-color: var(--accent-green);
    box-shadow: 0 0 5px var(--accent-green);
}

.status-card.status-unhealthy {
    border-color: var(--accent-red);
    box-shadow: 0 0 5px var(--accent-red);
}

/* Terminal Output */
.terminal-output {
    background: #000;
    border: 1px solid var(--accent-cyan);
    height: 400px;
    overflow-y: auto;
    padding: 10px;
    font-family: 'Fira Code', monospace;
    font-size: 14px;
}

.terminal-line {
    margin-bottom: 5px;
}

.terminal-success {
    color: var(--accent-green);
}

.terminal-error {
    color: var(--accent-red);
}

.terminal-info {
    color: var(--accent-cyan);
}

.terminal-command {
    color: #ffff00;
}

/* WebSocket Status */
.ws-connected {
    color: var(--accent-green);
}

.ws-disconnected {
    color: var(--accent-red);
}
```

---

## 📝 Documentation Maintenance Instructions

**⚠️ When UI components change, update this documentation immediately:**

### State Management Changes
- [ ] Update `window.APEX.state` structure examples
- [ ] Update `setState`/`getState` usage patterns
- [ ] Update `onStateChange` handler examples
- [ ] Test state changes trigger correct UI updates

### WebSocket Integration Changes
- [ ] Update `handleWebSocketMessage` message type examples
- [ ] Update connection/reconnection logic
- [ ] Update real-time update patterns
- [ ] Verify WebSocket message types match backend

### API Integration Changes
- [ ] Update command execution patterns
- [ ] Update endpoint URLs and request formats
- [ ] Update response handling examples
- [ ] Test API coherence with backend routes

### Template Structure Changes
- [ ] Update HTML template examples
- [ ] Update CSS selector references
- [ ] Update JavaScript DOM manipulation
- [ ] Verify all component integrations work

### New UI Components Added
- [ ] Add component documentation section
- [ ] Add state management patterns
- [ ] Add API integration examples
- [ ] Add CSS styling patterns

### Testing UI Changes
```bash
# Test UI functionality
cd apex/
python3 apex.py --web &

# Open browser to http://localhost:8000
# Test each UI component:
# - Environment switching
# - Provider authentication
# - Command execution  
# - WebSocket connection
# - Terminal output
# - Status updates

kill %1
```