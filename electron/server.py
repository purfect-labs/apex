#!/usr/bin/env python3
"""
Simple APEX server for Electron app
Just runs your regular APEX web server
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and run your normal APEX server
from web.main import run_server

if __name__ == "__main__":
    print("🚀 Starting APEX server for Electron...")
    
    # Set environment variables to prevent terminal auth and loops
    os.environ['APEX_NATIVE_MODE'] = '1'
    os.environ['APEX_NO_TERMINAL_AUTH'] = '1'
    os.environ['APEX_DISABLE_AUTO_AUTH'] = '1'
    os.environ['APEX_NO_CLOUD_INIT'] = '1'
    os.environ['AWS_PROFILE'] = 'none'
    os.environ['DISABLE_AWS_AUTH'] = '1'
    os.environ['DISABLE_GCP_AUTH'] = '1'
    
    run_server()
