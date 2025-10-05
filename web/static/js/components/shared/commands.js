// APEX Command Execution

// Execute proper API command
async function executeApiCommand(action, provider, params = {}) {
    const now = Date.now();
    
    // Prevent rapid successive executions (debounce)
    if (now - window.APEX.lastExecutionTime() < 500) {
        console.log('Ignoring rapid click');
        return;
    }
    
    if (window.APEX.isExecuting()) {
        window.APEX.addTerminalLine('System', '⚠️ Command already executing, please wait...', 'warning');
        return;
    }
    
    // Set executing flag and timestamp immediately to prevent duplicates
    window.APEX.setLastExecutionTime(now);
    window.APEX.setExecuting(true);
    updateStopButton();
    
    // Get current UI state for environment context
    const activeEnvToggle = document.querySelector('.env-toggle.active');
    const environment = activeEnvToggle ? activeEnvToggle.getAttribute('data-env') : 'dev';
    
    console.log(`Executing API: ${action} on ${provider} for ${environment}`);
    
    // Add to command history 
    const commandDesc = `${provider}.${action}(${environment})`;
    window.APEX.commandHistory.push(commandDesc);
    window.APEX.updateCommandHistory();
    
    // Show command in terminal
    window.APEX.addTerminalLine('apex', commandDesc, 'command');
    
    try {
        // Add environment to params
        const fullParams = { env: environment, ...params };
        
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: action,
                provider: provider,
                params: fullParams
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.APEX.addTerminalLine('System', `✅ ${result.message || 'Command initiated successfully'}`, 'success');
        } else {
            window.APEX.addTerminalLine('System', `❌ ${result.error || 'Command failed'}`, 'error');
        }
        
    } catch (error) {
        console.error('API Error:', error);
        window.APEX.addTerminalLine('Error', `Failed to execute ${action}: ${error.message}`, 'error');
    } finally {
        window.APEX.setExecuting(false);
        updateStopButton();
    }
}

// Keep old executeCommand as executeRawCommand for fallback
function executeRawCommand(command) {
    const now = Date.now();
    
    // Prevent rapid successive executions (debounce)
    if (now - window.APEX.lastExecutionTime() < 500) {
        console.log('Ignoring rapid click on raw command');
        return;
    }
    
    if (window.APEX.isExecuting()) {
        window.APEX.addTerminalLine('System', '⚠️ Command already executing, please wait...', 'warning');
        return;
    }
    
    // Set timestamp and executing flag
    window.APEX.setLastExecutionTime(now);
    
    console.log(`Executing raw: ${command}`);
    
    // Get current UI state
    const activeEnvToggle = document.querySelector('.env-toggle.active');
    const environment = activeEnvToggle ? activeEnvToggle.getAttribute('data-env') : 'dev';
    const activeCloudToggle = document.querySelector('.cloud-toggle.active');
    const cloud = activeCloudToggle ? activeCloudToggle.getAttribute('data-cloud') : 'aws';
    
    // Add command to history
    window.APEX.commandHistory.push(command);
    window.APEX.updateCommandHistory();
    
    // Show command in terminal
    window.APEX.addTerminalLine('apex', command, 'command');
    
    window.APEX.setExecuting(true);
    updateStopButton();
    
    // Send via WebSocket with UI state
    const ws = window.APEX.ws();
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'execute_command',
            data: {
                command: command,
                context: 'general',
                cloud: cloud,
                env: environment
            }
        }));
    } else {
        // Fallback to REST API
        fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: command,
                context: 'general',
                cloud: cloud,
                env: environment
            })
        }).then(response => response.json())
        .then(data => {
            console.log('Command sent:', data);
        })
        .catch(error => {
            console.error('Error:', error);
            window.APEX.addTerminalLine('Error', `Failed to execute command: ${error}`, 'error');
            window.APEX.setExecuting(false);
            updateStopButton();
        });
    }
}

// Initialize command buttons
function initializeCommandButtons() {
    // Remove existing event listeners to prevent duplicates
    document.querySelectorAll('.command-btn').forEach(btn => {
        // Clone node to remove all event listeners
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
    });
    
    // Add fresh event listeners
    document.querySelectorAll('.command-btn').forEach(btn => {
        btn.addEventListener('click', function(event) {
            // Prevent multiple clicks
            if (this.disabled || window.APEX.isExecuting()) {
                return;
            }
            
            const action = this.getAttribute('data-action');
            const provider = this.getAttribute('data-provider');
            const command = this.getAttribute('data-command');
            
            if (action && provider) {
                // Use new API pattern
                executeApiCommand(action, provider);
            } else if (command) {
                // Fallback to old pattern for buttons not yet converted
                executeRawCommand(command);
            }
        }, { once: false });
    });
}

// Initialize terminal input
function initializeTerminalInput() {
    const input = document.getElementById('terminal-input');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const command = this.value.trim();
                if (command) {
                    executeRawCommand(command);
                    this.value = '';
                }
            }
        });
    }
}

// Environment switching functions
function switchCloud(cloud) {
    window.APEX.addTerminalLine('System', `Switching to ${cloud.toUpperCase()}...`, 'success');
    window.APEX.updateSystemStatus({ cloud: cloud.toUpperCase() });
    
    // Update toggle buttons
    document.querySelectorAll('.cloud-toggle').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-cloud') === cloud) {
            btn.classList.add('active');
        }
    });
}

function switchEnvironment(env) {
    window.APEX.addTerminalLine('System', `Switching to ${env} environment...`, 'success');
    
    // Update toggle buttons with environment-specific colors
    document.querySelectorAll('.env-toggle').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-env') === env) {
            btn.classList.add('active');
        }
    });
    
    // Update status display
    window.APEX.updateSystemStatus({ environment: env });
}

// Make functions available globally
window.executeApiCommand = executeApiCommand;
window.executeRawCommand = executeRawCommand;
window.initializeCommandButtons = initializeCommandButtons;
window.initializeTerminalInput = initializeTerminalInput;
window.switchCloud = switchCloud;
window.switchEnvironment = switchEnvironment;