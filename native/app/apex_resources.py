#!/usr/bin/env python3
"""
APEX Resource Bundling System
Embeds HTML, CSS, JS, and other web assets into the Python executable
"""

import base64
import gzip
import mimetypes
import os
import json
from pathlib import Path
from typing import Dict, Optional, Union, List
import logging

logger = logging.getLogger(__name__)


class ResourceManager:
    """Manages embedded web resources for APEX application"""
    
    def __init__(self):
        self._resources: Dict[str, Dict] = {}
        self._load_embedded_resources()
    
    def _load_embedded_resources(self):
        """Load resources that were embedded during build process"""
        # This will be populated by the build script
        # For now, we'll try to load from files if they exist
        try:
            # Check if we're running from source or bundled
            if self._is_bundled():
                # Load from embedded resources
                self._load_from_embedded()
            else:
                # Load from file system (development mode)
                self._load_from_filesystem()
        except Exception as e:
            logger.error(f"Failed to load resources: {e}")
    
    def _is_bundled(self) -> bool:
        """Check if we're running from a PyInstaller bundle"""
        return hasattr(__import__('sys'), '_MEIPASS')
    
    def _load_from_embedded(self):
        """Load resources from embedded data (production mode)"""
        try:
            # This will be replaced by the build script with actual embedded data
            embedded_data = EMBEDDED_RESOURCES if 'EMBEDDED_RESOURCES' in globals() else {}
            self._resources = embedded_data
            logger.info(f"Loaded {len(self._resources)} embedded resources")
        except Exception as e:
            logger.error(f"Failed to load embedded resources: {e}")
    
    def _load_from_filesystem(self):
        """Load resources from filesystem (development mode)"""
        base_path = Path(__file__).parent / "web"
        
        # Define resource paths to scan
        resource_paths = [
            "templates",
            "static", 
            "public"
        ]
        
        for resource_dir in resource_paths:
            dir_path = base_path / resource_dir
            if dir_path.exists():
                self._scan_directory(dir_path, base_path)
        
        logger.info(f"Loaded {len(self._resources)} resources from filesystem")
    
    def _scan_directory(self, directory: Path, base_path: Path):
        """Recursively scan directory for web resources"""
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # Calculate relative path from web directory
                rel_path = file_path.relative_to(base_path)
                web_path = "/" + str(rel_path).replace("\\", "/")
                
                # Only include web assets
                if self._is_web_asset(file_path):
                    try:
                        self._add_resource_from_file(web_path, file_path)
                    except Exception as e:
                        logger.warning(f"Failed to load resource {file_path}: {e}")
    
    def _is_web_asset(self, file_path: Path) -> bool:
        """Check if file is a web asset we should bundle"""
        web_extensions = {
            '.html', '.htm', '.css', '.js', '.json',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.woff', '.woff2', '.ttf', '.eot',
            '.txt', '.md'
        }
        return file_path.suffix.lower() in web_extensions
    
    def _add_resource_from_file(self, web_path: str, file_path: Path):
        """Add a resource from a file"""
        try:
            content = file_path.read_bytes()
            
            # Compress content
            compressed = gzip.compress(content)
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Store resource info
            self._resources[web_path] = {
                'content': base64.b64encode(compressed).decode('ascii'),
                'mime_type': mime_type,
                'size': len(content),
                'compressed_size': len(compressed),
                'encoding': 'gzip'
            }
            
        except Exception as e:
            logger.error(f"Failed to process resource {web_path}: {e}")
    
    def get_resource(self, path: str) -> Optional[Dict]:
        """Get resource by path"""
        # Normalize path
        if not path.startswith('/'):
            path = '/' + path
        
        return self._resources.get(path)
    
    def get_resource_content(self, path: str) -> Optional[bytes]:
        """Get decompressed resource content"""
        resource = self.get_resource(path)
        if not resource:
            return None
        
        try:
            # Decode base64 and decompress
            compressed_data = base64.b64decode(resource['content'])
            if resource.get('encoding') == 'gzip':
                return gzip.decompress(compressed_data)
            else:
                return compressed_data
        except Exception as e:
            logger.error(f"Failed to decompress resource {path}: {e}")
            return None
    
    def get_resource_info(self, path: str) -> Optional[Dict]:
        """Get resource metadata without content"""
        resource = self.get_resource(path)
        if not resource:
            return None
        
        return {
            'mime_type': resource['mime_type'],
            'size': resource['size'],
            'compressed_size': resource['compressed_size'],
            'encoding': resource.get('encoding')
        }
    
    def list_resources(self) -> List[str]:
        """List all available resource paths"""
        return list(self._resources.keys())
    
    def get_stats(self) -> Dict:
        """Get resource bundling statistics"""
        if not self._resources:
            return {'count': 0, 'total_size': 0, 'compressed_size': 0}
        
        total_size = sum(r['size'] for r in self._resources.values())
        compressed_size = sum(r['compressed_size'] for r in self._resources.values())
        
        return {
            'count': len(self._resources),
            'total_size': total_size,
            'compressed_size': compressed_size,
            'compression_ratio': compressed_size / total_size if total_size > 0 else 0
        }


# Global resource manager instance
_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """Get global resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def create_resource_bundle_script():
    """Create a build script to embed resources"""
    script_content = '''#!/usr/bin/env python3
"""
Build script to create embedded resource bundle for APEX
Run this before building with PyInstaller
"""

import base64
import gzip
import mimetypes
import os
from pathlib import Path

def create_embedded_resources():
    """Create embedded resources Python file"""
    
    base_path = Path("web")
    resources = {}
    
    # Define resource paths to scan
    resource_paths = ["templates", "static", "public"]
    
    for resource_dir in resource_paths:
        dir_path = base_path / resource_dir
        if dir_path.exists():
            print(f"Scanning {dir_path}...")
            scan_directory(dir_path, base_path, resources)
    
    # Generate Python file with embedded resources
    output_content = f"""# Auto-generated embedded resources for APEX
# DO NOT EDIT - Generated by build_resources.py

EMBEDDED_RESOURCES = {repr(resources)}
"""
    
    # Write to apex_resources_embedded.py
    output_file = Path("apex_resources_embedded.py")
    output_file.write_text(output_content)
    
    # Print statistics
    total_files = len(resources)
    total_size = sum(r['size'] for r in resources.values())
    compressed_size = sum(r['compressed_size'] for r in resources.values())
    
    print(f"\\n✅ Embedded {total_files} resources")
    print(f"📊 Original size: {total_size:,} bytes")
    print(f"🗜️  Compressed size: {compressed_size:,} bytes")
    print(f"📉 Compression ratio: {compressed_size/total_size:.1%}")
    print(f"💾 Saved to: {output_file}")
    
    return output_file

def scan_directory(directory: Path, base_path: Path, resources: dict):
    """Recursively scan directory for web resources"""
    web_extensions = {
        '.html', '.htm', '.css', '.js', '.json',
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot',
        '.txt', '.md'
    }
    
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in web_extensions:
            # Calculate relative path from web directory
            rel_path = file_path.relative_to(base_path)
            web_path = "/" + str(rel_path).replace("\\\\", "/")
            
            try:
                content = file_path.read_bytes()
                compressed = gzip.compress(content)
                
                # Determine MIME type
                mime_type, _ = mimetypes.guess_type(str(file_path))
                if not mime_type:
                    mime_type = "application/octet-stream"
                
                resources[web_path] = {
                    'content': base64.b64encode(compressed).decode('ascii'),
                    'mime_type': mime_type,
                    'size': len(content),
                    'compressed_size': len(compressed),
                    'encoding': 'gzip'
                }
                
                print(f"  📄 {web_path} ({len(content)} → {len(compressed)} bytes)")
                
            except Exception as e:
                print(f"  ❌ Failed to process {file_path}: {e}")

if __name__ == "__main__":
    print("🔨 Building APEX resource bundle...")
    print("=" * 50)
    
    create_embedded_resources()
    
    print("\\n🚀 Resource bundle created successfully!")
    print("You can now run PyInstaller to build the executable.")
'''
    
    script_path = Path("build_resources.py")
    script_path.write_text(script_content)
    
    return script_path


if __name__ == "__main__":
    # Development/testing
    manager = get_resource_manager()
    stats = manager.get_stats()
    
    print("APEX Resource Manager")
    print("=" * 30)
    print(f"Resources: {stats['count']}")
    print(f"Total size: {stats['total_size']:,} bytes")
    print(f"Compressed: {stats['compressed_size']:,} bytes")
    print(f"Ratio: {stats['compression_ratio']:.1%}")
    print()
    
    # List some resources
    resources = manager.list_resources()
    if resources:
        print("Sample resources:")
        for path in sorted(resources)[:10]:
            info = manager.get_resource_info(path)
            print(f"  {path} ({info['mime_type']}, {info['size']} bytes)")
        
        if len(resources) > 10:
            print(f"  ... and {len(resources) - 10} more")
    else:
        print("No resources found. Run in development mode or create bundle.")
        
        # Create build script
        script = create_resource_bundle_script()
        print(f"\\nCreated build script: {script}")
        print("Run: python build_resources.py")