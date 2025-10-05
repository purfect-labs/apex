const { app, BrowserWindow, Menu, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const net = require('net');

class APEXNativeApp {
    constructor() {
        this.mainWindow = null;
        this.pythonProcess = null;
        this.serverPort = 8000;
        this.serverReady = false;
        
        // Handle app events
        app.whenReady().then(() => this.init());
        app.on('window-all-closed', () => this.quit());
        app.on('activate', () => this.createWindow());
        app.on('before-quit', () => this.cleanup());
    }

    async init() {
        console.log('🚀 APEX Native App Starting...');
        
        // Start Python server
        await this.startPythonServer();
        
        // Wait for server to be ready
        await this.waitForServer();
        
        // Create main window
        this.createWindow();
        
        // Setup native menus
        this.setupMenu();
    }

    async startPythonServer() {
        console.log('🐍 Starting Python server...');
        
        try {
            // Find Python and apex_app.py
            const pythonPath = this.getPythonPath();
            const appPath = this.getAppPath();
            
            console.log(`Python: ${pythonPath}`);
            console.log(`App: ${appPath}`);
            
            // Start Python process
            this.pythonProcess = spawn(pythonPath, [appPath], {
                cwd: path.dirname(appPath),
                env: { 
                    ...process.env,
                    PYTHONPATH: path.dirname(appPath)
                },
                detached: false
            });
            
            this.pythonProcess.stdout.on('data', (data) => {
                console.log(`[Python] ${data.toString().trim()}`);
                if (data.toString().includes('Server started successfully')) {
                    this.serverReady = true;
                }
            });
            
            this.pythonProcess.stderr.on('data', (data) => {
                console.error(`[Python Error] ${data.toString().trim()}`);
            });
            
            this.pythonProcess.on('exit', (code) => {
                console.log(`Python process exited with code ${code}`);
            });
            
            console.log('✅ Python server process started');
            
        } catch (error) {
            console.error('❌ Failed to start Python server:', error);
            dialog.showErrorBox('Server Error', `Failed to start APEX server: ${error.message}`);
        }
    }

    getPythonPath() {
        // In development
        if (!app.isPackaged) {
            return 'python3';
        }
        
        // In packaged app
        const resourcesPath = process.resourcesPath;
        return path.join(resourcesPath, 'venv', 'bin', 'python');
    }

    getAppPath() {
        // In development
        if (!app.isPackaged) {
            return path.join(__dirname, 'server.py');
        }
        
        // In packaged app
        const resourcesPath = process.resourcesPath;
        return path.join(resourcesPath, 'server.py');
    }

    async waitForServer() {
        console.log('⏳ Waiting for server to be ready...');
        
        for (let i = 0; i < 150; i++) { // 15 second timeout
            try {
                await this.checkServerHealth();
                console.log('✅ Server is ready!');
                return;
            } catch (error) {
                if (i % 10 === 0) { // Log every second
                    console.log(`Server check ${i+1}/150: ${error.message}`);
                }
                await this.sleep(100);
            }
        }
        
        console.error('❌ Server failed to start, opening window anyway...');
        // Don't throw - open window anyway and let it retry
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
            
            req.on('error', (err) => {
                reject(err);
            });
            
            req.setTimeout(1000, () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });
        });
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async retryServerConnection() {
        if (!this.mainWindow) return;
        
        let attempts = 0;
        const maxAttempts = 30; // 30 seconds
        
        const tryConnection = async () => {
            try {
                await this.checkServerHealth();
                console.log('🔄 Server ready, reloading window...');
                this.mainWindow.reload();
                return;
            } catch (error) {
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(tryConnection, 1000); // Try again in 1 second
                } else {
                    console.log('⚠️ Server connection retry limit reached');
                }
            }
        };
        
        // Start trying after a short delay
        setTimeout(tryConnection, 2000);
    }

    createWindow() {
        if (this.mainWindow) {
            this.mainWindow.show();
            return;
        }

        console.log('🖥️ Creating main window...');
        
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
            icon: path.join(__dirname, 'assets', 'icon.png'),
            show: false // Don't show until ready
        });

        // Load APEX interface
        this.mainWindow.loadURL(`http://127.0.0.1:${this.serverPort}`);

        // Show when ready
        this.mainWindow.once('ready-to-show', () => {
            console.log('✅ Window ready, showing APEX interface');
            this.mainWindow.show();
            
            if (process.env.NODE_ENV === 'development') {
                this.mainWindow.webContents.openDevTools();
            }
            
            // If server isn't ready, keep trying to reload
            this.retryServerConnection();
        });
        
        // Handle load failures
        this.mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
            console.log(`Failed to load: ${errorDescription}`);
            this.retryServerConnection();
        });

        // Handle window closed
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        // Handle external links
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
    }

    setupMenu() {
        const template = [
            {
                label: 'APEX',
                submenu: [
                    {
                        label: 'About APEX',
                        click: () => this.showAbout()
                    },
                    { type: 'separator' },
                    {
                        label: 'Preferences...',
                        accelerator: 'CmdOrCtrl+,',
                        click: () => this.showPreferences()
                    },
                    { type: 'separator' },
                    {
                        label: 'Hide APEX',
                        accelerator: 'CmdOrCtrl+H',
                        role: 'hide'
                    },
                    {
                        label: 'Hide Others',
                        accelerator: 'CmdOrCtrl+Alt+H',
                        role: 'hideothers'
                    },
                    {
                        label: 'Show All',
                        role: 'unhide'
                    },
                    { type: 'separator' },
                    {
                        label: 'Quit APEX',
                        accelerator: 'CmdOrCtrl+Q',
                        click: () => this.quit()
                    }
                ]
            },
            {
                label: 'Edit',
                submenu: [
                    { role: 'undo' },
                    { role: 'redo' },
                    { type: 'separator' },
                    { role: 'cut' },
                    { role: 'copy' },
                    { role: 'paste' },
                    { role: 'selectall' }
                ]
            },
            {
                label: 'View',
                submenu: [
                    { role: 'reload' },
                    { role: 'forcereload' },
                    { role: 'toggledevtools' },
                    { type: 'separator' },
                    { role: 'resetzoom' },
                    { role: 'zoomin' },
                    { role: 'zoomout' },
                    { type: 'separator' },
                    { role: 'togglefullscreen' }
                ]
            },
            {
                label: 'Window',
                submenu: [
                    { role: 'minimize' },
                    { role: 'close' }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    showAbout() {
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'About APEX',
            message: 'APEX Command Center',
            detail: 'Version 3.0.0\n\nA powerful cloud operations interface for AWS, GCP, and Kubernetes management.\n\n© 2024 APEX. All rights reserved.'
        });
    }

    showPreferences() {
        // TODO: Implement preferences window
        console.log('Preferences not yet implemented');
    }

    cleanup() {
        console.log('🧹 Cleaning up...');
        
        if (this.pythonProcess) {
            console.log('Terminating Python server...');
            this.pythonProcess.kill('SIGTERM');
            
            setTimeout(() => {
                if (!this.pythonProcess.killed) {
                    this.pythonProcess.kill('SIGKILL');
                }
            }, 3000);
        }
    }

    quit() {
        console.log('👋 APEX shutting down...');
        this.cleanup();
        app.quit();
    }
}

// Create app instance
new APEXNativeApp();