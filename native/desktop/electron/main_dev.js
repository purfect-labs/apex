const { app, BrowserWindow, Menu, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class APEXNativeApp {
    constructor() {
        this.mainWindow = null;
        this.apexProcess = null;
        this.serverPort = 8000; // Use standard APEX port
        this.serverReady = false;
        
        app.whenReady().then(() => this.init());
        app.on('window-all-closed', () => this.quit());
        app.on('activate', () => this.createWindow());
        app.on('before-quit', () => this.cleanup());
    }

    async init() {
        console.log('🚀 APEX Unified Native App Starting...');
        
        await this.startAPEXServer();
        await this.waitForServer();
        this.createWindow();
        this.setupMenu();
    }

    async startAPEXServer() {
        console.log('⚙️ Starting APEX server...');
        
        try {
            const executablePath = this.getAPEXExecutablePath();
            console.log(`APEX Executable: ${executablePath}`);
            
            if (!fs.existsSync(executablePath)) {
                throw new Error(`APEX executable not found: ${executablePath}`);
            }

            // Start APEX process with default port (8000)
            this.apexProcess = spawn(executablePath, [], {
                env: process.env,
                detached: false
            });
            
            this.apexProcess.stdout.on('data', (data) => {
                const output = data.toString().trim();
                console.log(`[APEX] ${output}`);
                if (output.includes('Uvicorn running')) {
                    this.serverReady = true;
                }
            });
            
            this.apexProcess.stderr.on('data', (data) => {
                console.error(`[APEX Error] ${data.toString().trim()}`);
            });
            
            this.apexProcess.on('exit', (code) => {
                console.log(`APEX process exited with code ${code}`);
            });
            
            console.log('✅ APEX server process started');
            
        } catch (error) {
            console.error('❌ Failed to start APEX server:', error);
            dialog.showErrorBox('Server Error', `Failed to start APEX server: ${error.message}`);
        }
    }

    getAPEXExecutablePath() {
        if (app.isPackaged) {
            return path.join(process.resourcesPath, 'apex_app');
        } else {
            // Development mode - use the built executable
            return path.join(__dirname, 'resources', 'apex_app');
        }
    }

    async waitForServer() {
        console.log('⏳ Waiting for APEX server...');
        
        for (let i = 0; i < 150; i++) {
            try {
                await this.checkServerHealth();
                console.log('✅ APEX server is ready!');
                return;
            } catch (error) {
                await this.sleep(100);
            }
        }
        console.error('❌ APEX server failed to start');
    }

    checkServerHealth() {
        return new Promise((resolve, reject) => {
            const http = require('http');
            const req = http.get(`http://127.0.0.1:${this.serverPort}/api/status`, (res) => {
                if (res.statusCode === 200) {
                    resolve();
                } else {
                    reject(new Error(`Server returned ${res.statusCode}`));
                }
                req.destroy();
            });
            
            req.on('error', reject);
            req.setTimeout(1000, () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });
        });
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    createWindow() {
        if (this.mainWindow) {
            this.mainWindow.show();
            return;
        }

        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1000,
            minHeight: 600,
            titleBarStyle: 'default',
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                preload: path.join(__dirname, 'preload.js')
            },
            show: false
        });

        this.mainWindow.loadURL(`http://127.0.0.1:${this.serverPort}`);
        
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            console.log('✅ APEX window ready');
        });
        
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });
    }

    setupMenu() {
        const template = [
            {
                label: 'APEX',
                submenu: [
                    { role: 'about' },
                    { type: 'separator' },
                    { role: 'quit' }
                ]
            },
            {
                label: 'Edit',
                submenu: [
                    { role: 'copy' },
                    { role: 'paste' },
                    { role: 'selectall' }
                ]
            },
            {
                label: 'View',
                submenu: [
                    { role: 'reload' },
                    { role: 'toggledevtools' },
                    { type: 'separator' },
                    { role: 'togglefullscreen' }
                ]
            }
        ];
        
        Menu.setApplicationMenu(Menu.buildFromTemplate(template));
    }

    cleanup() {
        if (this.apexProcess) {
            this.apexProcess.kill();
        }
    }

    quit() {
        this.cleanup();
        if (process.platform !== 'darwin') {
            app.quit();
        }
    }
}

new APEXNativeApp();
