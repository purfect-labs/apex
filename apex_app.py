#!/usr/bin/env python3
"""
APEX Native macOS Application
Creates a native macOS window using PyWebView to display the web interface
Handles license validation and starts embedded FastAPI server
"""

import asyncio
import logging
import os
import signal
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

import webview
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Import our modules
from apex_license import check_license, prompt_for_license, APEXLicenseManager
from apex_resources import get_resource_manager

# Add parent directory to path for web import
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from web.main import APEXMainApp

# Configure comprehensive file logging
import logging.handlers
from datetime import datetime

# Create log file with timestamp
log_file = f"/tmp/apex_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Setup file handler for detailed logging
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
file_handler.setFormatter(file_formatter)

# Setup console handler for basic output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)
logger.info(f"Debug logging to: {log_file}")


def run_server_process(port, log_file_path):
    """Server function that can be pickled for multiprocessing"""
    import logging
    import uvicorn
    import sys
    from pathlib import Path
    
    # Setup logging in the process
    file_handler = logging.FileHandler(log_file_path, mode='a')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(formatter)
    
    process_logger = logging.getLogger('server_process')
    process_logger.addHandler(file_handler)
    process_logger.setLevel(logging.DEBUG)
    
    try:
        process_logger.info(f"Server process starting on port {port}")
        
        # Add parent directory to path for web import
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Import and create the full APEX app
        process_logger.info("Loading full APEX application...")
        from web.main import APEXMainApp
        
        apex_main = APEXMainApp()
        app = apex_main.app
        
        process_logger.info("✅ Full APEX application loaded successfully")
        
        # Start uvicorn with the full APEX app
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
            use_colors=False,
            reload=False,
            workers=1
        )
        
    except Exception as e:
        process_logger.error(f"Server process failed: {e}")
        import traceback
        process_logger.error(traceback.format_exc())
        raise


class APEXNativeApp:
    """Native macOS application wrapper for APEX"""
    
    def __init__(self):
        self.port = 8000
        self.server = None
        self.server_thread = None
        self.webview_window = None
        self.license_info = None
        self.resource_manager = get_resource_manager()
        
    def check_license_validation(self) -> bool:
        """Check if application has valid license"""
        try:
            # ALWAYS use demo license to avoid keychain issues in native app
            logger.info("Using 7-day demo license")
            
            # Calculate 7 days from now
            from datetime import datetime, timedelta
            expires_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            self.license_info = {
                'valid': True,
                'user_name': 'Trial User', 
                'user_email': 'trial@apex.dev',
                'features': ['basic', 'advanced', 'premium'],
                'license_type': '7-day-trial',
                'expires': expires_date,
                'activated': True
            }
            return True
        except Exception as e:
            logger.error(f"License setup failed: {e}")
            # Fallback license
            self.license_info = {
                'valid': True, 
                'user_name': 'Demo User', 
                'user_email': 'demo@apex.dev',
                'license_type': 'demo'
            }
            return True
    
    def _is_packaged(self) -> bool:
        """Check if running from PyInstaller bundle"""
        return hasattr(sys, '_MEIPASS')
    
    def show_license_dialog(self) -> bool:
        """Show license activation dialog"""
        try:
            # For GUI mode, we'll use webview to show license dialog
            # For now, fall back to console prompt
            success, info = prompt_for_license()
            if success:
                self.license_info = info
                return True
            return False
        except Exception as e:
            logger.error(f"License dialog failed: {e}")
            return False
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application using the full APEX web application"""
        
        logger.debug("create_fastapi_app() called")
        logger.info("Loading full APEX application...")
        
        from web.main import APEXMainApp
        
        # Create the main APEX app with full functionality
        apex_main = APEXMainApp()
        app = apex_main.app
        logger.info("✅ Successfully loaded full APEX application")
        
        # Add native app specific endpoints
        self._add_native_endpoints_to_app(app)
        
        logger.debug(f"Returning FastAPI app: {app}")
        return app
    
    def _add_native_endpoints_to_app(self, app: FastAPI):
        """Add native app specific endpoints to the full APEX app"""
        # Add license info endpoint for native app
        @app.get("/api/license/info")
        async def get_license_info():
            return {
                "valid": True,
                "user_name": self.license_info.get('user_name'),
                "user_email": self.license_info.get('user_email'),
                "expires": self.license_info.get('expires'),
                "features": self.license_info.get('features', []),
                "license_type": self.license_info.get('license_type')
            }
        
        @app.get("/api/app/info")
        async def get_app_info():
            return {
                "name": "APEX",
                "version": "3.0.0",
                "mode": "native_app",
                "platform": sys.platform,
                "license_valid": self.license_info is not None
            }
    
    def create_apex_fallback_app(self) -> FastAPI:
        """Create fallback APEX app that serves your actual templates"""
        from fastapi.staticfiles import StaticFiles
        from fastapi import FastAPI, Request
        from fastapi.responses import FileResponse, HTMLResponse
        import os
        from pathlib import Path
        
        app = FastAPI(title="APEX Command Center", version="3.0.0")
        
        # Get the web directory path
        web_dir = Path(__file__).parent / "web"
        
        # Serve the main APEX interface
        @app.get("/", response_class=HTMLResponse)
        async def get_index():
            # Serve your actual APEX template
            template_path = web_dir / "templates" / "apex_compact.html"
            if template_path.exists():
                with open(template_path, 'r') as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                # Try the main template as fallback
                template_path = web_dir / "templates" / "apex_index.html"
                if template_path.exists():
                    with open(template_path, 'r') as f:
                        content = f.read()
                    return HTMLResponse(content=content)
                else:
                    # Last fallback
                    return HTMLResponse(content=self.get_minimal_interface())
        
        # Mount static files if they exist
        static_path = web_dir / "static"
        if static_path.exists():
            app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
            
        public_path = web_dir / "public" 
        if public_path.exists():
            app.mount("/public", StaticFiles(directory=str(public_path)), name="public")
        
        # Add your APEX API endpoints that your templates expect
        @app.get("/api/status")
        async def get_status():
            return {
                "timestamp": "2024-10-03T21:58:00Z",
                "aws": {"status": "ready"},
                "gcp": {"status": "ready"},
                "git": {"status": "available"},
                "kubernetes": {"status": "ready"},
                "config": {"aws_profiles": ["dev", "stage", "prod"], "gcp_projects": {}}
            }
        
        @app.get("/api/config")
        async def get_config():
            return {
                "aws_profiles": ["dev", "stage", "prod"],
                "gcp_projects": {"dev": "dev-project", "prod": "prod-project"},
                "database_configs": {},
                "timestamp": "2024-10-03T21:58:00Z"
            }
        
        @app.post("/api/auth")
        async def auth_endpoint(request: dict = None):
            return {"status": "starting", "provider": "aws"}
        
        @app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket, client_id: str):
            await websocket.accept()
            await websocket.send_text('{"type": "status", "data": {"connected": true}}')
            try:
                while True:
                    await websocket.receive_text()
            except:
                pass
        
        return app
    
    def get_minimal_interface(self) -> str:
        """Minimal interface when APEX templates aren't found"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>APEX Command Center</title>
            <style>
                body { font-family: -apple-system, sans-serif; margin: 40px; }
                h1 { color: #007AFF; }
            </style>
        </head>
        <body>
            <h1>⚡ APEX Command Center</h1>
            <p>Native macOS Application Running</p>
            <p>Your APEX templates will load here when available.</p>
        </body>
        </html>
        """
    
    def get_license_status_html(self) -> str:
        """Get license status HTML"""
        if self.license_info:
            return f"""
            <div class="license-info">
                <div><strong>✅ License Active</strong></div>
                <div>User: {self.license_info.get('user_name', 'Licensed User')}</div>
                <div>Email: {self.license_info.get('user_email', 'N/A')}</div>
                <div>Features: {', '.join(self.license_info.get('features', []))}</div>
            </div>
            """
        else:
            return """
            <div class="status">
                <div>⚠️ No active license</div>
                <button class="btn" onclick="alert('License management available in full version')">Activate License</button>
            </div>
            """
        
        # Add CORS middleware for local webview
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Override static file serving to use embedded resources
        @app.middleware("http")
        async def serve_embedded_resources(request: Request, call_next):
            """Serve embedded resources instead of files"""
            
            # Check if this is a request for static resources
            if request.url.path.startswith('/static/') or request.url.path.startswith('/templates/'):
                resource_path = request.url.path
                
                # Try to get resource from embedded bundle
                content = self.resource_manager.get_resource_content(resource_path)
                if content:
                    info = self.resource_manager.get_resource_info(resource_path)
                    headers = {
                        'Content-Type': info['mime_type'],
                        'Content-Length': str(len(content))
                    }
                    if info.get('encoding') == 'gzip':
                        headers['Content-Encoding'] = 'gzip'
                    
                    return Response(content, headers=headers)
            
            # Continue with normal request processing
            response = await call_next(request)
            return response
        
        # Add license info endpoint
        @app.get("/api/license/info")
        async def get_license_info():
            """Get current license information"""
            if self.license_info:
                return {
                    "valid": True,
                    "user_name": self.license_info.get('user_name'),
                    "user_email": self.license_info.get('user_email'),
                    "expires": self.license_info.get('expires'),
                    "features": self.license_info.get('features', []),
                    "license_type": self.license_info.get('license_type')
                }
            else:
                return {"valid": False}
        
        # Add application info
        @app.get("/api/app/info")
        async def get_app_info():
            """Get application information"""
            return {
                "name": "APEX",
                "version": "3.0.0",
                "mode": "native_app",
                "platform": sys.platform,
                "license_valid": self.license_info is not None
            }
        
        return app
    
    def start_server(self):
        """Start FastAPI server in background thread with improved reliability"""
        import socket
        
        # Check if port is available first
        def is_port_available(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                    return True
                except OSError:
                    return False
        
        # Find an available port if 8000 is taken
        original_port = self.port
        for port_attempt in range(self.port, self.port + 10):
            if is_port_available(port_attempt):
                self.port = port_attempt
                logger.info(f"Using port {self.port}")
                break
        else:
            logger.error("No available ports found")
            return False
        # Use multiprocessing with external function to avoid blocking
        logger.info("Starting server process...")
        import multiprocessing
        self.server_process = multiprocessing.Process(
            target=run_server_process, 
            args=(self.port, log_file)
        )
        self.server_process.daemon = True
        self.server_process.start()
        
        # Wait for server to be ready with better error handling
        logger.info("Waiting for server to be ready...")
        import urllib.request
        import urllib.error
        
        for i in range(100):  # Wait up to 10 seconds
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/status", timeout=0.5) as response:
                    if response.getcode() == 200:
                        logger.info(f"✅ Server started successfully on port {self.port}")
                        return True
            except (urllib.error.URLError, Exception) as e:
                if i % 20 == 0:  # Log every 2 seconds
                    logger.debug(f"Server check {i+1}/100: {e}")
                time.sleep(0.1)
        
        logger.error("❌ Server failed to start within 10 second timeout")
        return False
    
    def create_webview_window(self):
        """Create native macOS window with improved stability"""
        
        logger.debug(f"create_webview_window() called")
        logger.info(f"Creating window for URL: http://127.0.0.1:{self.port}")
        
        # Window configuration optimized for macOS
        window_config = {
            'title': 'APEX Command Center',
            'url': f'http://127.0.0.1:{self.port}',
            'width': 1200,
            'height': 800,
            'min_size': (900, 600),
            'resizable': True,
            'fullscreen': False,
            'minimized': False,
            'on_top': False,
            'shadow': True,
            'focus': True,
            'text_select': True
        }
        
        # Create JavaScript API for window
        class WindowAPI:
            def __init__(self, app_instance):
                self.app = app_instance
            
            def get_license_info(self):
                return self.app.license_info
            
            def quit_app(self):
                logger.info("Quit requested from window")
                self.app.quit()
                
            def get_server_info(self):
                return {
                    'port': self.app.port,
                    'status': 'running' if self.app.server else 'stopped'
                }
        
        # Configure webview settings with comprehensive defaults to prevent crashes
        logger.debug("Configuring webview settings...")
        webview.settings = {
            'ALLOW_DOWNLOADS': False,
            'ALLOW_FILE_URLS': True, 
            'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
            'DEBUG': False,  # Disable debug to avoid dev tools issues
            'SHOW_DEFAULT_MENUS': True,
            'IGNORE_SSL_ERRORS': True,
            'DRAG_REGION_SELECTOR': None,
            'OPEN_DEVTOOLS_IN_DEBUG': False,
            'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
            'ALLOW_FILE_DOWNLOADS': False,
            'JS_EXCEPTIONS': True,
            'SHADOW': True,
            'ON_TOP': False,
            'TEXT_SELECT': True
        }
        logger.debug(f"WebView settings configured: {webview.settings}")
        
        # Create window with API
        logger.debug("Creating WindowAPI instance...")
        api = WindowAPI(self)
        logger.debug(f"WindowAPI created: {api}")
        
        logger.debug(f"About to call webview.create_window with config: {window_config}")
        self.webview_window = webview.create_window(
            js_api=api,
            **window_config
        )
        logger.debug(f"webview.create_window returned: {self.webview_window}")
        
        logger.info("✅ WebView window configured successfully")
        return self.webview_window
    
    def _detect_electron_mode(self) -> bool:
        """Detect if we're running inside Electron wrapper"""
        try:
            # Check environment variables that Electron sets
            if os.environ.get('ELECTRON_RUN_AS_NODE'):
                return True
            
            # Check for Electron-specific process names in parent processes
            import psutil
            current_process = psutil.Process()
            parent = current_process.parent()
            
            if parent and ('electron' in parent.name().lower() or 
                          'apex command center' in parent.name().lower()):
                return True
            
            # Check for Electron resources directory structure
            app_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            electron_indicators = [
                os.path.join(app_path, '..', '..', '..', 'Resources', 'apex_app'),
                os.environ.get('APEX_ELECTRON_MODE') == '1'
            ]
            
            return any(os.path.exists(path) if isinstance(path, str) else path for path in electron_indicators)
            
        except Exception as e:
            logger.debug(f"Electron detection failed: {e}")
            return False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for clean shutdown"""
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal")
            self.quit()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def quit(self):
        """Clean shutdown of application"""
        logger.info("Shutting down APEX application...")
        
        if hasattr(self, 'server_process') and self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.join(timeout=2)
            except:
                pass
        
        if self.server:
            try:
                self.server.should_exit = True
            except:
                pass
        
        if self.webview_window:
            try:
                webview.destroy_window()
            except:
                pass
        
        # Give processes time to cleanup
        time.sleep(0.5)
        sys.exit(0)
    
    def run(self):
        """Main application entry point with comprehensive debug logging"""
        logger.info("⚙️ APEX Native Application Starting...")
        logger.info("====================================")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Platform: {sys.platform}")
        logger.debug(f"Working directory: {os.getcwd()}")
        
        # Skip complex webview settings to avoid crashes
        logger.debug("Using default webview settings")
        
        try:
            # Setup signal handlers
            logger.debug("Setting up signal handlers...")
            self.setup_signal_handlers()
            logger.debug("✅ Signal handlers set up")
            
            # Check license (now always succeeds with demo license)
            logger.info("🔑 Validating license...")
            logger.debug("Calling check_license_validation()...")
            if not self.check_license_validation():
                logger.error("❌ License validation failed. Exiting.")
                sys.exit(1)
            logger.debug("✅ License validation completed")
            
            # Start FastAPI server
            logger.info("🌍 Starting web server...")
            logger.debug("Calling start_server()...")
            if not self.start_server():
                logger.error("❌ Failed to start web server. Exiting.")
                sys.exit(1)
            logger.debug("✅ Web server started successfully")
            
            # Give server a moment to fully initialize
            logger.debug("Waiting 0.5s for server initialization...")
            time.sleep(0.5)
            logger.debug("✅ Server initialization wait completed")
            
            # Auto-detect mode: Check if we should run PyWebView or server-only mode
            logger.info(f"✅ Server ready at: http://127.0.0.1:{self.port}")
            
            # Detect if running standalone or with Electron
            running_with_electron = self._detect_electron_mode()
            
            if running_with_electron:
                logger.info("🎆 Electron detected - running in server-only mode")
                logger.info("⏳ Keeping server running for Electron...")
                # Keep server running for Electron
                while True:
                    time.sleep(1)
            else:
                logger.info("🗺️ Standalone mode - launching PyWebView window")
                # Create and start PyWebView window
                logger.debug("Creating PyWebView window...")
                window = self.create_webview_window()
                if window:
                    logger.info("🎨 Starting PyWebView application...")
                    webview.start(debug=True)
                else:
                    logger.error("❌ Failed to create PyWebView window")
                    # Fallback to browser mode
                    logger.info("🌍 Falling back to browser mode...")
                    webbrowser.open(f'http://127.0.0.1:{self.port}')
                    # Keep server running
                    while True:
                        time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("⏹️ Interrupted by user")
        except Exception as e:
            logger.error(f"❌ Application error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Fallback: try to open in browser
            logger.info("🌍 Attempting browser fallback...")
            try:
                webbrowser.open(f'http://127.0.0.1:{self.port}')
                logger.info("ℹ️ Server will continue running. Press Ctrl+C to stop.")
                
                # Keep server running
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("⏹️ Browser mode interrupted")
        
        finally:
            logger.info("🧹 Cleaning up...")
            self.quit()


def main():
    """Application entry point"""
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--browser":
            # Launch in browser mode instead of native window
            from web.main import run_server
            run_server()
            return
        elif sys.argv[1] == "--license":
            # License management mode
            success, info = prompt_for_license()
            if success:
                print("✅ License activated successfully!")
            else:
                print("❌ License activation failed.")
            return
    
    # Create and run native application
    app = APEXNativeApp()
    app.run()


if __name__ == "__main__":
    main()