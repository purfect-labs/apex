// GCP Kali Dashboard Functions

let kaliConnectedEnvs = [];

function getSelectedKaliEnvs() {
    const checkboxes = document.querySelectorAll('.kali-env-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.getAttribute('data-env'));
}

async function connectKali() {
    const selectedEnvs = getSelectedKaliEnvs();
    
    if (selectedEnvs.length === 0) {
        window.APEX.addTerminalLine('System', '⚠️ No environments selected for Kali connection', 'warning');
        return;
    }
    
    window.APEX.addTerminalLine('System', `🚀 Connecting Kali for environments: ${selectedEnvs.join(', ')}`, 'success');
    
    // First, stop any existing port forwards to prevent conflicts
    window.APEX.addTerminalLine('System', '🧠 Cleaning up existing port forwards...', 'warning');
    await stopKaliPortForwards();
    
    for (const env of selectedEnvs) {
        try {
            // Use the proper controller pattern
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'kali_port_forward',
                    provider: 'gcp',
                    params: { env: env }
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.APEX.addTerminalLine('System', `✅ Kali port forwarding initiated for ${env}`, 'success');
                if (!kaliConnectedEnvs.includes(env)) {
                    kaliConnectedEnvs.push(env);
                }
            } else {
                window.APEX.addTerminalLine('System', `❌ Failed to connect Kali for ${env}: ${result.error}`, 'error');
            }
        } catch (error) {
            window.APEX.addTerminalLine('System', `❌ Error connecting Kali for ${env}: ${error.message}`, 'error');
        }
    }
}

function openKaliDashboards() {
    if (kaliConnectedEnvs.length === 0) {
        window.APEX.addTerminalLine('System', '⚠️ No Kali environments connected. Please connect first.', 'warning');
        return;
    }
    
    const portMap = { 'dev': 20002, 'stage': 20003, 'prod': 20004 };
    let openedCount = 0;
    
    for (const env of kaliConnectedEnvs) {
        const port = portMap[env];
        const url = `http://localhost:${port}`;
        
        try {
            window.open(url, `kiali-${env}`);
            openedCount++;
            window.APEX.addTerminalLine('System', `🔗 Opened Kali dashboard for ${env}: ${url}`, 'success');
        } catch (error) {
            window.APEX.addTerminalLine('System', `❌ Failed to open dashboard for ${env}: ${error.message}`, 'error');
        }
    }
    
    if (openedCount > 0) {
        window.APEX.addTerminalLine('System', `✅ Opened ${openedCount} Kali dashboard(s)`, 'success');
    }
}

async function stopKaliPortForwards() {
    window.APEX.addTerminalLine('System', '🛑 Stopping all Kali port forwards...', 'warning');
    
    try {
        const response = await fetch('/api/gcp/kali/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.APEX.addTerminalLine('System', '✅ All Kali port forwards stopped', 'success');
            kaliConnectedEnvs = [];
        } else {
            window.APEX.addTerminalLine('System', `❌ Failed to stop port forwards: ${result.error}`, 'error');
        }
    } catch (error) {
        window.APEX.addTerminalLine('System', `❌ Error stopping port forwards: ${error.message}`, 'error');
    }
}

async function checkKaliStatus() {
    window.APEX.addTerminalLine('System', '📊 Checking Kali pod and port forward status...', 'success');
    
    try {
        const response = await fetch('/api/gcp/kali/status');
        const result = await response.json();
        
        if (result.success) {
            if (result.status && result.status.length > 0) {
                result.status.forEach(envStatus => {
                    const statusEmoji = envStatus.connected ? '✅' : '❌';
                    const statusMsg = envStatus.connected ? 'Connected' : 'Not connected';
                    window.APEX.addTerminalLine('System', `${statusEmoji} ${envStatus.env}: ${statusMsg} (port ${envStatus.port})`, 
                        envStatus.connected ? 'success' : 'warning');
                });
            } else {
                window.APEX.addTerminalLine('System', '⚠️ No Kali connections found', 'warning');
            }
        } else {
            window.APEX.addTerminalLine('System', `❌ Failed to check status: ${result.error}`, 'error');
        }
    } catch (error) {
        window.APEX.addTerminalLine('System', `❌ Error checking status: ${error.message}`, 'error');
    }
}

// Make functions available globally
window.connectKali = connectKali;
window.openKaliDashboards = openKaliDashboards;
window.stopKaliPortForwards = stopKaliPortForwards;
window.checkKaliStatus = checkKaliStatus;