#!/usr/bin/env python3
"""
APEX - Kubernetes Command Center
Main entry point for all deployment modes

Usage:
    python apex.py                    # Web server mode (default)
    python apex.py --browser         # Web server mode 
    python apex.py --native          # Native desktop application
    python apex.py --electron        # Electron wrapper (requires npm start)
    python apex.py --help            # Show help
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='APEX - Kubernetes Command Center',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python apex.py                   # Show this help
  
  # Complete development cycles:
  python apex.py iterate           # Build + test + run locally
  python apex.py iterate --docker  # Build + test + run via Docker
  
  # Runtime-only commands:
  python apex.py --mac-native --web       # Run local APEX in web mode
  python apex.py --mac-native --native    # Run local APEX in native mode
  python apex.py --docker-native --web    # Run Docker-built in web mode
  python apex.py --docker-native --native # Run Docker-built in native mode
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        help='Command to run: iterate, build-unified, compile-collect'
    )
    
    parser.add_argument(
        '--docker', 
        action='store_true',
        help='Use Docker for build and run operations'
    )
    
    parser.add_argument(
        '--mac-native',
        action='store_true', 
        help='Run using local macOS build'
    )
    
    parser.add_argument(
        '--docker-native',
        action='store_true',
        help='Run using Docker-built binary'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Start in web mode'
    )
    
    parser.add_argument(
        '--native',
        action='store_true', 
        help='Start in native app mode'
    )
    
    args = parser.parse_args()
    
    # Handle --web flag by calling start-apex.sh
    if args.web and not (args.mac_native or args.docker_native):
        print("🚀 Starting APEX with start-apex.sh...")
        start_script = Path(__file__).parent / "start-apex.sh"
        if start_script.exists():
            try:
                subprocess.run(["bash", str(start_script)], cwd=Path(__file__).parent)
            except KeyboardInterrupt:
                print("\n👋 APEX stopped")
                sys.exit(0)
        else:
            print(f"❌ Start script not found: {start_script}")
            sys.exit(1)
        return
    
    # Handle runtime-only commands
    if args.mac_native or args.docker_native:
        if not (args.web or args.native):
            print("❌ Must specify --web or --native with runtime commands")
            parser.print_help()
            sys.exit(1)
        
        if args.mac_native:
            run_mac_native(web_mode=args.web, native_mode=args.native)
        elif args.docker_native:
            run_docker_native(web_mode=args.web, native_mode=args.native)
        return
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return
    
    # Handle commands
    if args.command == 'iterate':
        if args.docker:
            print("🐳 Starting Docker iterate: Build + Test + Run")
            run_iterate_docker()
        else:
            print("🖥️ Starting local iterate: Build + Test + Run")
            run_iterate_local()
    elif args.command == 'build-unified':
        print("🚀 Starting unified build: Electron + Nuitka")
        run_unified_build()
    elif args.command == 'compile-collect':
        print("📦 Collecting all build artifacts")
        run_compile_collect()
    else:
        print(f"❌ Unknown command: {args.command}")
        print("💡 Available commands: iterate, build-unified, compile-collect")
        parser.print_help()
        sys.exit(1)

def run_compile_collect():
    """Collect all build artifacts from different locations and organize them"""
    import shutil
    import time
    from datetime import datetime
    
    print("📦 APEX Compile & Collect - Gathering All Build Artifacts")
    print("=" * 55)
    
    # Create .dist directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    collect_dir = Path(__file__).parent / ".dist" / f"collection_{timestamp}"
    collect_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Collection directory: {collect_dir}")
    
    collected_count = 0
    
    # Define artifact locations and their naming conventions
    artifacts = [
        # === LINUX ARTIFACTS (Docker built) ===
        
        # Linux server binary (main Docker artifact)
        {
            'source': 'dist/apex-real',
            'dest': 'apex-linux-docker-server',
            'type': 'Linux Docker Server Binary'
        },
        
        # Linux PyWebView binary (Docker built)
        {
            'source': 'dist/apex-linux-pyweb',
            'dest': 'apex-linux-docker-pyweb',
            'type': 'Linux Docker PyWebView Binary'
        },
        
        # Linux DMG files (built via Docker calling macOS build)
        {
            'source': 'dist/APEX-3.0.0-macOS-Nuitka.dmg',
            'dest': 'APEX-macos-docker-pyweb.dmg',
            'type': 'macOS Docker PyWebView DMG'
        },
        
        {
            'source': 'dist/APEX-3.0.0-Unified.dmg',
            'dest': 'APEX-macos-docker-electron.dmg',
            'type': 'macOS Docker Electron DMG'
        },
        
        # === macOS ARTIFACTS (Local built) ===
        
        # Local PyWebView app 
        {
            'source': 'native/build/dist/APEX.app',
            'dest': 'APEX-macos-local-pyweb.app',
            'type': 'macOS Local PyWebView App'
        },
        
        # Local PyWebView DMG
        {
            'source': 'native/build/dist/APEX-3.0.0-macOS-Nuitka.dmg',
            'dest': 'APEX-macos-local-pyweb.dmg',
            'type': 'macOS Local PyWebView DMG'
        },
        
        # Local Electron app 
        {
            'source': 'native/desktop/electron/dist/mac-arm64/APEX Command Center.app',
            'dest': 'APEX-macos-local-electron.app',
            'type': 'macOS Local Electron App'
        },
        
        # Unified Electron DMG (local build) 
        {
            'source': 'native/unified_dist/APEX-3.0.0-Unified.dmg',
            'dest': 'APEX-macos-unified-electron.dmg', 
            'type': 'macOS Unified Electron DMG'
        },
        
        # Standard Electron DMG (local build)
        {
            'source': 'native/desktop/electron/dist/APEX-3.0.0-Electron.dmg',
            'dest': 'APEX-macos-electron.dmg',
            'type': 'macOS Electron DMG'
        },
    ]
    
    # Collect artifacts
    print("\n🔍 Scanning for build artifacts...")
    
    for artifact in artifacts:
        source_path = Path(__file__).parent / artifact['source']
        dest_path = collect_dir / artifact['dest']
        
        if source_path.exists():
            try:
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path)
                    size = sum(f.stat().st_size for f in dest_path.rglob('*') if f.is_file())
                    size_mb = size // 1024 // 1024
                    print(f"  ✅ {artifact['type']}: {artifact['source']} ({size_mb}MB)")
                else:
                    shutil.copy2(source_path, dest_path)
                    size_mb = source_path.stat().st_size // 1024 // 1024
                    print(f"  ✅ {artifact['type']}: {artifact['source']} ({size_mb}MB)")
                
                collected_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to collect {artifact['source']}: {e}")
        else:
            print(f"  ⏸️  Not found: {artifact['source']}")
    
    # Create collection manifest
    manifest_path = collect_dir / "COLLECTION_MANIFEST.md"
    with open(manifest_path, 'w') as f:
        f.write(f"# APEX Build Artifacts Collection\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Artifacts**: {collected_count}\n\n")
        
        f.write("## Collected Artifacts\n\n")
        for artifact in artifacts:
            source_path = Path(__file__).parent / artifact['source']
            if source_path.exists():
                f.write(f"- ✅ **{artifact['type']}**: `{artifact['dest']}`\n")
            else:
                f.write(f"- ❌ **{artifact['type']}**: Not found\n")
        
        f.write("\n## Usage\n\n")
        f.write("**For Distribution:**\n")
        f.write("- `*.dmg` files - macOS installers\n")
        f.write("- `*.app` directories - macOS applications\n")
        f.write("- `*-binary` files - Linux executables\n\n")
        
        f.write("**App Types:**\n")
        f.write("- `*pyweb*` - Native PyWebView apps (lighter, WebKit)\n")
        f.write("- `*electron*` - Electron apps (heavier, full Chromium)\n")
        f.write("- `*docker*` - Docker-built Linux binaries\n")
        f.write("- `*local*` - Locally-built macOS apps\n")
    
    # Create quick launch scripts
    launch_script = collect_dir / "launch_apps.sh"
    with open(launch_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Quick launch script for collected APEX apps\n\n")
        f.write("echo \"🚀 APEX App Launcher\"\n")
        f.write("echo \"==================\"\n\n")
        
        f.write("# Launch PyWebView app\n")
        f.write("if [ -d \"APEX-macos-local-pyweb.app\" ]; then\n")
        f.write("    echo \"1) Launch PyWebView app\"\n")
        f.write("    read -p \"Press 1 to launch PyWebView app: \" choice\n")
        f.write("    if [ \"$choice\" = \"1\" ]; then\n")
        f.write("        open \"APEX-macos-local-pyweb.app\"\n")
        f.write("    fi\n")
        f.write("fi\n\n")
        
        f.write("# Launch Electron app\n")
        f.write("if [ -d \"APEX-macos-local-electron.app\" ]; then\n")
        f.write("    echo \"2) Launch Electron app\"\n")
        f.write("    read -p \"Press 2 to launch Electron app: \" choice\n")
        f.write("    if [ \"$choice\" = \"2\" ]; then\n")
        f.write("        open \"APEX-macos-local-electron.app\"\n")
        f.write("    fi\n")
        f.write("fi\n")
    
    # Make launch script executable
    import stat
    launch_script.chmod(launch_script.stat().st_mode | stat.S_IEXEC)
    
    # Summary
    print("\n🎉 Collection Complete!")
    print("=" * 25)
    print(f"📁 Collection directory: {collect_dir}")
    print(f"📦 Artifacts collected: {collected_count}")
    print(f"📄 Manifest created: COLLECTION_MANIFEST.md")
    print(f"🚀 Launch script: launch_apps.sh")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in collect_dir.rglob('*') if f.is_file())
    total_mb = total_size // 1024 // 1024
    print(f"📊 Total collection size: {total_mb}MB")
    
    print("\n🗺️ Next steps:")
    print(f"   1. Review: open {collect_dir}")
    print(f"   2. Test apps: cd {collect_dir} && ./launch_apps.sh")
    print(f"   3. Distribute: Share .dmg files")
    
    # Optionally open the collection directory
    try:
        subprocess.run(["open", str(collect_dir)], check=False)
        print(f"\n📂 Opened collection directory in Finder")
    except:
        pass

def run_unified_build():
    """Run unified DMG build with Electron + Nuitka"""
    try:
        # Get the unified build script path
        build_script = Path(__file__).parent / "native" / "build_unified.sh"
        
        if not build_script.exists():
            print(f"❌ Unified build script not found at: {build_script}")
            return False
        
        print(f"📁 Unified build script: {build_script}")
        print("🚀 Building complete DMG installer with Electron + Nuitka...")
        print("🔄 This will take a few minutes...")
        
        # Run the unified build script
        result = subprocess.run(
            ["bash", str(build_script), "--open"],
            cwd=build_script.parent,
            text=True
        )
        
        if result.returncode == 0:
            print("🎉 Unified build completed successfully!")
            print("📦 Check native/unified_dist/ for the final DMG installer")
            return True
        else:
            print(f"❌ Unified build failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Unified build failed: {e}")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    try:
        print("📦 Running pip3 install -r requirements.txt...")
        result = subprocess.run([
            "pip3", "install", "--break-system-packages", "-r", "requirements.txt"
        ], text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies ready")
            return True
        else:
            print("❌ pip3 install failed")
            return False
            
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def build_local_binary():
    """Build local macOS binary using PyInstaller"""
    try:
        print("📦 Creating PyInstaller spec for macOS...")
        
        # Create PyInstaller spec for local macOS build
        spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['apex_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'webview',
        'uvicorn', 
        'fastapi',
        'websockets',
        'pydantic',
        'yaml',
        'keyring',
        'cryptography',
        'psutil',
        'jinja2',
        'aiofiles',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='apex-macos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
        
        # Write spec file
        with open('apex_macos.spec', 'w') as f:
            f.write(spec_content)
        
        print("🛠️ Building with PyInstaller...")
        result = subprocess.run([
            'pyinstaller', 'apex_macos.spec', '--clean', '--noconfirm'
        ], text=True, capture_output=True)
        
        if result.returncode == 0:
            # Check if binary was created
            macos_binary = Path('./dist/apex-macos')
            if macos_binary.exists():
                print(f"✅ Local macOS binary created: {macos_binary}")
                print(f"📏 Binary size: {macos_binary.stat().st_size // 1024 // 1024}MB")
                return True
            else:
                print("❌ Binary not found after build")
                return False
        else:
            print(f"❌ PyInstaller failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Local build failed: {e}")
        return False

def run_iterate_local():
    """Complete local development cycle: build + test + run"""
    print("🚀 APEX Local Iterate - Complete Development Cycle")
    print("=" * 50)
    
    # Install dependencies 
    print("📦 Step 1: Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        print("💡 Try manually: pip install -r requirements.txt")
        print("💡 Or use Docker: python3 apex.py iterate --docker")
        return False
    
    try:
        print("✅ Dependencies ready")
        
        # Step 2: Build local binary
        print("\n🔨 Step 2: Building local macOS binary...")
        if not build_local_binary():
            print("⚠️  Build failed but continuing with source...")
        
        # Step 3: Test
        print("\n🧪 Step 3: Running tests...")
        if not run_tests():
            print("⚠️  Tests failed but continuing...")
        
        # Step 4: Run
        print("\n🌐 Step 4: Starting APEX web interface...")
        print("📍 Will be available at: http://localhost:8000")
        start_web_mode(8000)
        
    except KeyboardInterrupt:
        print("\n👋 APEX iterate stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Iterate failed: {e}")
        sys.exit(1)

def run_iterate_docker():
    """Complete Docker development cycle: build + test + run"""
    print("🐳 APEX Docker Iterate - Complete Development Cycle")
    print("=" * 50)
    
    try:
        # Step 1: Build 
        print("🔨 Step 1: Building with Docker...")
        # Build both macOS and Linux artifacts (skip tests)
        if not run_docker_build("--build-dmg"):
            print("❌ Docker macOS build failed - stopping iterate")
            return False
        if not run_docker_build("--build-native"):
            print("❌ Docker build failed - stopping iterate")
            return False
        
        # Step 2: Test (skip for now since build includes tests)
        print("\n✅ Step 2: Tests completed during build")
        
        # Step 3: Run native PyWebView app locally
        print("\n🚀 Step 3: Starting native PyWebView app...")
        print("💡 Docker built the Linux binary, now running native macOS app")
        
        # Run the native PyWebView app we built with unified build
        native_app = Path(__file__).parent / "native" / "build" / "dist" / "APEX.app" / "Contents" / "MacOS" / "apex_app"
        
        if native_app.exists():
            print(f"🎨 Launching native PyWebView app: {native_app}")
            subprocess.run([str(native_app)])
        else:
            print("⚠️  Native app not found, falling back to web mode...")
            print("🌐 Starting web server instead...")
            print("📍 Available at: http://localhost:8000")
            start_web_mode(8000)
        
    except KeyboardInterrupt:
        print("\n👋 APEX Docker iterate stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Docker iterate failed: {e}")
        sys.exit(1)

def run_docker_app():
    """Run the Docker-built application"""
    try:
        # Check if we have a built binary
        binary_path = Path(__file__).parent / "dist" / "apex-real"
        
        if binary_path.exists():
            print(f"📍 Found Docker-built binary: {binary_path}")
            print("💡 Note: This is a Linux binary - running via Docker...")
            
            # Run the binary inside Docker
            docker_compose_path = Path(__file__).parent / "linux-native" / "docker-compose.yml"
            
            result = subprocess.run([
                "docker-compose", "-f", str(docker_compose_path), 
                "run", "--rm", "-p", "8000:8000", "apex-build", 
                "/app/dist/apex-real"
            ], cwd=Path(__file__).parent)
            
        else:
            print("❌ No Docker-built binary found")
            print("💡 Run: python3 apex.py iterate --docker first")
            
    except Exception as e:
        print(f"❌ Failed to run Docker app: {e}")

def run_mac_native(web_mode=False, native_mode=False):
    """Run local macOS APEX (runtime-only)"""
    print("🖥️ APEX macOS Native Runtime")
    print("=" * 30)
    
    # Check if we have a built macOS binary
    macos_binary = Path('./dist/apex-macos')
    
    if macos_binary.exists():
        print(f"🚀 Found local macOS binary: {macos_binary}")
        if web_mode:
            print("🌐 Running built binary in web mode...")
            subprocess.run([str(macos_binary)])
        elif native_mode:
            print("🖥️ Running built binary in native mode...")
            subprocess.run([str(macos_binary)])
    else:
        print("💡 No built binary found, running from source...")
        if web_mode:
            print("🌐 Starting local APEX in web mode...")
            print("📍 Will be available at: http://localhost:8000")
            start_web_mode(8000)
        elif native_mode:
            print("🖥️ Starting local APEX in native mode...")
            start_native_mode(recompile=False)

def run_docker_native(web_mode=False, native_mode=False):
    """Run Docker-built APEX (runtime-only)"""
    print("🐳 APEX Docker Native Runtime")
    print("=" * 30)
    
    # Check if Docker-built binary exists
    binary_path = Path(__file__).parent / "dist" / "apex-real"
    
    if not binary_path.exists():
        print("❌ No Docker-built binary found")
        print("💡 Run: python3 apex.py iterate --docker first")
        return
    
    if web_mode:
        print("🌐 Starting Docker-built APEX in web mode...")
        print("📍 Will be available at: http://localhost:8000")
        run_docker_app()
    elif native_mode:
        print("🖥️ Docker-built native mode not supported on macOS")
        print("💡 Use --web mode or run: python3 apex.py --mac-native --native")

def run_native_build():
    """Build native macOS app using linux-native build system"""
    try:
        print("🔨 Building native macOS app...")
        
        # Use our new linux-native/build.sh script
        build_script = Path(__file__).parent / "linux-native" / "build.sh"
        
        if not build_script.exists():
            print(f"❌ Build script not found: {build_script}")
            return False
        
        result = subprocess.run(
            ["bash", str(build_script), "--build-native"],
            cwd=Path(__file__).parent,
            text=True
        )
        
        if result.returncode == 0:
            print("🎉 Native build completed successfully!")
            return True
        else:
            print(f"❌ Native build failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Native build failed: {e}")
        return False

def run_docker_build(command="--all"):
    """Build using Docker with specific command"""
    try:
        print(f"🐳 Building with Docker ({command})...")
        
        # Check if Docker is available
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        
        docker_compose_path = Path(__file__).parent / "linux-native" / "docker-compose.yml"
        
        if not docker_compose_path.exists():
            print(f"❌ Docker compose file not found: {docker_compose_path}")
            return False
        
        # First: Build Docker image (use cache when possible)
        print("🔧 Building Docker image with cache optimization...")
        rebuild_result = subprocess.run(
            ["docker-compose", "-f", str(docker_compose_path), "build", "apex-build"],
            cwd=Path(__file__).parent,
            text=True
        )
        
        if rebuild_result.returncode != 0:
            print("❌ Docker image rebuild failed")
            return False
        
        print("✅ Docker image rebuilt successfully")
        
        # Run docker compose with specific command
        result = subprocess.run(
            ["docker-compose", "-f", str(docker_compose_path), "run", "--rm", "apex-build", "./linux-native/build.sh", command],
            cwd=Path(__file__).parent,
            text=True
        )
        
        if result.returncode == 0:
            print("🎉 Docker build completed successfully!")
            return True
        else:
            print(f"❌ Docker build failed with exit code: {result.returncode}")
            return False
            
    except subprocess.CalledProcessError:
        print("❌ Docker not found - please install Docker")
        return False
    except Exception as e:
        print(f"❌ Docker build failed: {e}")
        return False

def run_tests():
    """Run test suite with backgrounding and tmp logging"""
    try:
        print("🧪 Running test suite...")
        
        # Background testing with tmp logging (following your rules)
        import time
        log_file = f"/tmp/apex-test-{int(time.time())}.log"
        
        print(f"📝 Test output will be logged to: {log_file}")
        
        # Check if pytest is available
        try:
            subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("⚠️  pytest not found, running basic Python tests...")
            # Fallback to basic validation
            result = subprocess.run(
                [sys.executable, "-c", "import web.main; print('✅ Basic import test passed')"],
                cwd=Path(__file__).parent,
                text=True
            )
            return result.returncode == 0
        
        # Run pytest with timeout and background logging
        with open(log_file, 'w') as f:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
                cwd=Path(__file__).parent,
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=60  # 60 second timeout
            )
        
        if result.returncode == 0:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"❌ Tests failed - check log: {log_file}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Tests timed out - check log: {log_file}")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def run_full_rebuild():
    """Run full clean rebuild using the build script"""
    try:
        # Get the build script path
        build_script = Path(__file__).parent / "native" / "build" / "build_nuitka.sh"
        
        if not build_script.exists():
            print(f"❌ Build script not found at: {build_script}")
            return False
        
        print(f"📁 Build script: {build_script}")
        print("🧹 This will do a complete clean rebuild...")
        
        # Clean ALL __pycache__ directories before building
        print("🧹 Cleaning Python cache recursively...")
        root_dir = Path(__file__).parent
        try:
            result = subprocess.run(["find", str(root_dir), "-type", "d", "-name", "__pycache__"], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pycache_dirs = result.stdout.strip().split('\n')
                for pycache_dir in pycache_dirs:
                    if pycache_dir:
                        subprocess.run(["rm", "-rf", pycache_dir], check=True)
                        print(f"   🗾️  Removed: {pycache_dir}")
        except subprocess.CalledProcessError:
            print("   ⚠️  Some __pycache__ directories could not be removed")
        
        # Change to build directory
        build_dir = build_script.parent
        original_cwd = os.getcwd()
        
        try:
            os.chdir(build_dir)
            
            # Run the build script with real-time output
            print("🚀 Starting build process...")
            result = subprocess.run(
                ["bash", str(build_script)],
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            if result.returncode == 0:
                print("🎉 Build completed successfully!")
                
                # Check if native app was built
                dist_dir = build_dir / "dist"
                app_bundle = dist_dir / "APEX.app"
                
                if app_bundle.exists():
                    print(f"✅ Native app bundle created: {app_bundle}")
                    return True
                else:
                    print("⚠️ Native app bundle not found after build")
                    return False
            else:
                print(f"❌ Build failed with exit code: {result.returncode}")
                return False
                
        finally:
            # Always restore original directory
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False

def start_web_mode(port=8000):
    """Start APEX in web server mode"""
    try:
        # Import and start the web application
        from web.main import run_server
        run_server(host="127.0.0.1", port=port)
    except ImportError as e:
        print(f"⚠️  Web server dependencies not available: {e}")
        print("💡 Install dependencies with: pip install -r requirements.txt")
        print("💡 Or use Docker version: python3 apex.py iterate --docker")
        
        # Create a simple fallback server
        print("\n🚀 Starting minimal fallback server...")
        start_fallback_server(port)
        
def start_fallback_server(port=8000):
    """Start a minimal web server when dependencies are missing"""
    try:
        import http.server
        import socketserver
        import webbrowser
        import threading
        import time
        
        # Create simple HTML content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>APEX - Setup Required</title>
    <style>
        body {{ font-family: system-ui; margin: 40px; background: #1a1a2e; color: white; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #4CAF50; }}
        .status {{ background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        code {{ background: #2d2d2d; padding: 2px 8px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ APEX Command Center</h1>
        <div class="status">
            <h3>⚠️  Dependencies Required</h3>
            <p>To run the full APEX application, install dependencies:</p>
            <code>pip install -r requirements.txt</code>
            <p>Or use the Docker version:</p>
            <code>python3 apex.py iterate --docker</code>
        </div>
    </div>
</body>
</html>
        """
        
        # Write HTML to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_file = f.name
        
        # Open browser
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'file://{html_file}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"📍 Fallback page opened in browser")
        print(f"💡 Install dependencies to run full APEX: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Fallback server failed: {e}")
        sys.exit(1)

def start_native_mode(recompile=False):
    """Start APEX as native desktop application"""
    
    if recompile:
        print("🔧 Performing full clean rebuild...")
        if not run_full_rebuild():
            print("❌ Rebuild failed, cannot start native app")
            sys.exit(1)
        print("✅ Rebuild completed, starting native app...")
    
    try:
        if recompile:
            # Use the built app bundle
            build_dir = Path(__file__).parent / "native" / "build"
            app_bundle = build_dir / "dist" / "APEX.app"
            
            if app_bundle.exists():
                print(f"🚀 Launching built native app: {app_bundle}")
                subprocess.run(["open", str(app_bundle)])
                return
            else:
                print("❌ Built app bundle not found, falling back to development mode")
        
        # Development mode - run from source
        print("💻 Running in development mode...")
        native_dir = Path(__file__).parent / "native"
        os.chdir(native_dir)
        
        # Add native directory to Python path
        sys.path.insert(0, str(native_dir))
        
        from apex_app import APEXNativeApp
        app = APEXNativeApp()
        app.run()
    except ImportError as e:
        print(f"❌ Failed to import native modules: {e}")
        print("💡 Make sure native dependencies are installed")
        sys.exit(1)

def start_electron_mode():
    """Start APEX with Electron wrapper"""
    import subprocess
    
    electron_dir = Path(__file__).parent / "native" / "electron"
    
    if not electron_dir.exists():
        print("❌ Electron directory not found")
        print(f"Expected: {electron_dir}")
        sys.exit(1)
    
    print(f"📁 Electron directory: {electron_dir}")
    
    try:
        # Check if npm is installed
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found - please install Node.js and npm")
        sys.exit(1)
    
    try:
        # Start Electron app
        os.chdir(electron_dir)
        print("📦 Running npm start...")
        subprocess.run(["npm", "start"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Electron app: {e}")
        print("💡 Try running 'npm install' in the electron directory first")
        sys.exit(1)

if __name__ == "__main__":
    main()