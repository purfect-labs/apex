// APEX Core Functionality

// Global state
let isExecuting = false;
let currentProcess = null;
let commandHistory = [];
let ws = null;
let clientId = Math.random().toString(36).substr(2, 9);
let lastExecutionTime = 0;

// Initialize WebSocket connection
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function(event) {
        console.log('WebSocket connected');
        addTerminalLine('System', '🔗 Connected to APEX backend', 'success');
    };
    
    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
    
    ws.onclose = function(event) {
        console.log('WebSocket disconnected');
        addTerminalLine('System', '❌ Disconnected from backend', 'error');
        // Try to reconnect after 3 seconds
        setTimeout(initWebSocket, 3000);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        addTerminalLine('System', '⚠️ Connection error', 'warning');
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(message) {
    if (message.type === 'command_output') {
        const output = message.data.output || message.data;
        addTerminalLine('Output', output, 'success');
    } else if (message.type === 'command_error') {
        const error = message.data.error || message.data;
        addTerminalLine('Error', error, 'error');
    } else if (message.type === 'command_started') {
        addTerminalLine('System', `🚀 Started: ${message.data.command}`, 'success');
    } else if (message.type === 'command_completed') {
        isExecuting = false;
        updateStopButton();
        addTerminalLine('System', `✅ Command completed (${message.data.exit_code === 0 ? 'success' : 'error'})`, 
            message.data.exit_code === 0 ? 'success' : 'error');
    } else if (message.type === 'command_stopped') {
        isExecuting = false;
        updateStopButton();
        addTerminalLine('System', '🛑 Command stopped', 'warning');
    } else if (message.type === 'status_update') {
        updateSystemStatus(message.data);
    } else if (message.type === 'port_forward_started') {
        addTerminalLine('System', `🔗 Port forward started: ${message.data.service}:${message.data.port}`, 'success');
    } else if (message.type === 'port_forward_stopped') {
        addTerminalLine('System', `🚫 Port forward stopped: ${message.data.service}:${message.data.port}`, 'warning');
    }
    
    // License-related message handling
    if (window.APEX && window.APEX.Profile && window.APEX.Profile.handleWebSocketMessage) {
        window.APEX.Profile.handleWebSocketMessage(message);
    }
}

// Add line to terminal
function addTerminalLine(prefix, content, type = 'normal') {
    const output = document.getElementById('terminal-output');
    const line = document.createElement('div');
    line.className = 'terminal-line';
    
    const promptSpan = document.createElement('span');
    promptSpan.className = 'terminal-prompt';
    promptSpan.textContent = `⚡ apex $`;
    
    const contentSpan = document.createElement('span');
    contentSpan.className = `terminal-${type}`;
    
    // Special handling for license keys
    if (type === 'license-key') {
        contentSpan.innerHTML = content;
        contentSpan.style.cssText = `
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid var(--neon-green);
            border-radius: 4px;
            padding: 0.5rem;
            margin: 0.5rem 0;
            display: block;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 1px;
            color: var(--neon-green);
            font-weight: bold;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        `;
    } else {
        contentSpan.textContent = content;
    }
    
    line.appendChild(promptSpan);
    line.appendChild(contentSpan);
    output.appendChild(line);
    
    // Auto scroll
    output.scrollTop = output.scrollHeight;
}

// Clear terminal
function clearTerminal() {
    const output = document.getElementById('terminal-output');
    output.innerHTML = `
        <div class="terminal-line">
            <span class="terminal-prompt">⚡ apex $</span>
            <span class="terminal-success">Terminal cleared</span>
        </div>
    `;
}

// Stop command
function stopCommand() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'stop_command',
            data: {}
        }));
    }
    isExecuting = false;
    updateStopButton();
    addTerminalLine('System', '🛑 Command stopped', 'warning');
}

// Update stop button state
function updateStopButton() {
    const stopBtn = document.getElementById('stop-btn');
    if (stopBtn) {
        stopBtn.disabled = !isExecuting;
        stopBtn.style.opacity = isExecuting ? '1' : '0.5';
    }
}

// Update command history display
function updateCommandHistory() {
    const historyDiv = document.getElementById('command-history');
    if (historyDiv) {
        const recent = commandHistory.slice(-10).reverse();
        
        historyDiv.innerHTML = recent.map(cmd => 
            `<div style="color: var(--neon-green); margin-bottom: 0.3rem;">✅ ${cmd} (just now)</div>`
        ).join('');
    }
}

// Update system status
function updateSystemStatus(status) {
    if (status.cloud) {
        const cloudStatus = document.getElementById('cloud-status');
        if (cloudStatus) cloudStatus.textContent = status.cloud;
        const envCloud = document.getElementById('env-cloud');
        if (envCloud) envCloud.textContent = status.cloud;
    }
    if (status.environment) {
        const envStatus = document.getElementById('env-status');
        if (envStatus) envStatus.textContent = status.environment;
        const envName = document.getElementById('env-name');
        if (envName) envName.textContent = status.environment;
    }
    if (status.region) {
        const envRegion = document.getElementById('env-region');
        if (envRegion) envRegion.textContent = status.region;
    }
}

// Export functions for use by other modules
window.APEX = {
    initWebSocket,
    addTerminalLine,
    clearTerminal,
    stopCommand,
    updateCommandHistory,
    updateSystemStatus,
    isExecuting: () => isExecuting,
    setExecuting: (value) => isExecuting = value,
    commandHistory,
    ws: () => ws,
    clientId,
    lastExecutionTime: () => lastExecutionTime,
    setLastExecutionTime: (value) => lastExecutionTime = value
};