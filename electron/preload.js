const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // License management
    getLicenseStatus: () => ipcRenderer.invoke('license:status'),
    activateLicense: (key) => ipcRenderer.invoke('license:activate', key),
    
    // App info
    getAppVersion: () => ipcRenderer.invoke('app:version'),
    
    // Preferences
    openPreferences: () => ipcRenderer.invoke('preferences:open'),
    
    // External links
    openExternal: (url) => ipcRenderer.invoke('shell:openExternal', url)
});

// DOM ready enhancement
window.addEventListener('DOMContentLoaded', () => {
    // Add native app class to body for styling
    document.body.classList.add('apex-native-app');
    
    // Enhance the interface for native feel
    const style = document.createElement('style');
    style.textContent = `
        .apex-native-app {
            /* Native macOS styling improvements */
            -webkit-user-select: none;
            -webkit-app-region: no-drag;
        }
        
        /* Make certain elements draggable for window movement */
        .header, .toolbar {
            -webkit-app-region: drag;
        }
        
        /* Ensure interactive elements are not draggable */
        button, input, select, textarea, a {
            -webkit-app-region: no-drag;
        }
    `;
    document.head.appendChild(style);
    
    console.log('🖥️ APEX Native App UI Enhanced');
});