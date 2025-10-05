"""
Filesystem Manager
Central manager for handling multiple filesystem providers and routing operations
"""

import asyncio
from typing import Dict, List, Optional, Any, Type
from .base_filesystem import BaseFilesystem, FileMetadata
from .s3_filesystem import S3Filesystem
from .gcs_filesystem import GCSFilesystem

class FilesystemManager:
    """Central manager for filesystem providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseFilesystem] = {}
        self.default_provider: Optional[str] = None
        
        # Registry of available filesystem types
        self.filesystem_types: Dict[str, Type[BaseFilesystem]] = {
            'aws_s3': S3Filesystem,
            'gcp_gcs': GCSFilesystem,
        }
    
    async def register_provider(self, name: str, filesystem: BaseFilesystem, 
                               set_as_default: bool = False) -> bool:
        """Register a filesystem provider"""
        try:
            # Test authentication
            auth_result = await filesystem.authenticate()
            if not auth_result.get('success', False):
                raise Exception(f"Failed to authenticate filesystem: {auth_result.get('error')}")
            
            self.providers[name] = filesystem
            
            if set_as_default or not self.default_provider:
                self.default_provider = name
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to register provider '{name}': {str(e)}")
    
    async def create_and_register_s3(self, name: str, bucket_name: str, 
                                    region: str = 'us-west-2',
                                    aws_access_key_id: Optional[str] = None,
                                    aws_secret_access_key: Optional[str] = None,
                                    aws_session_token: Optional[str] = None,
                                    endpoint_url: Optional[str] = None,
                                    set_as_default: bool = False) -> bool:
        """Create and register an S3 filesystem provider"""
        s3_fs = S3Filesystem(
            bucket_name=bucket_name,
            region=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            endpoint_url=endpoint_url
        )
        
        return await self.register_provider(name, s3_fs, set_as_default)
    
    async def create_and_register_gcs(self, name: str, bucket_name: str,
                                     project_id: Optional[str] = None,
                                     credentials_path: Optional[str] = None,
                                     set_as_default: bool = False) -> bool:
        """Create and register a GCS filesystem provider"""
        gcs_fs = GCSFilesystem(
            bucket_name=bucket_name,
            project_id=project_id,
            credentials_path=credentials_path
        )
        
        return await self.register_provider(name, gcs_fs, set_as_default)
    
    def get_provider(self, name: Optional[str] = None) -> BaseFilesystem:
        """Get a filesystem provider by name, or default if name is None"""
        if name is None:
            name = self.default_provider
        
        if name is None:
            raise ValueError("No default provider set and no provider name specified")
        
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not registered")
        
        return self.providers[name]
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all registered providers"""
        provider_info = []
        
        for name, provider in self.providers.items():
            provider_info.append({
                'name': name,
                'type': provider.name,
                'is_default': name == self.default_provider,
                'authenticated': provider._authenticated
            })
        
        return provider_info
    
    async def get_status(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of a provider or all providers"""
        if provider_name:
            provider = self.get_provider(provider_name)
            return await provider.get_status()
        else:
            # Get status of all providers
            all_status = {}
            for name, provider in self.providers.items():
                try:
                    all_status[name] = await provider.get_status()
                except Exception as e:
                    all_status[name] = {
                        'error': str(e),
                        'accessible': False,
                        'provider': provider.name
                    }
            return all_status
    
    # Delegate common operations to default or specified provider
    async def list_files(self, path: str = "/", recursive: bool = False, 
                        max_results: int = 1000, provider: Optional[str] = None) -> List[FileMetadata]:
        """List files using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.list_files(path, recursive, max_results)
    
    async def get_file(self, path: str, provider: Optional[str] = None) -> bytes:
        """Get file using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.get_file(path)
    
    async def put_file(self, path: str, content: bytes, 
                      metadata: Optional[Dict[str, str]] = None, 
                      provider: Optional[str] = None) -> FileMetadata:
        """Put file using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.put_file(path, content, metadata)
    
    async def delete_file(self, path: str, provider: Optional[str] = None) -> bool:
        """Delete file using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.delete_file(path)
    
    async def file_exists(self, path: str, provider: Optional[str] = None) -> bool:
        """Check if file exists using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.file_exists(path)
    
    async def get_file_metadata(self, path: str, provider: Optional[str] = None) -> Optional[FileMetadata]:
        """Get file metadata using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.get_file_metadata(path)
    
    async def get_file_url(self, path: str, expires_in: int = 3600, 
                          provider: Optional[str] = None) -> Optional[str]:
        """Get presigned URL using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.get_file_url(path, expires_in)
    
    async def copy_file(self, source_path: str, dest_path: str, 
                       source_provider: Optional[str] = None,
                       dest_provider: Optional[str] = None) -> FileMetadata:
        """Copy file between providers or within same provider"""
        source_fs = self.get_provider(source_provider)
        dest_fs = self.get_provider(dest_provider)
        
        if source_fs == dest_fs:
            # Same provider - use native copy if available
            return await source_fs.copy_file(source_path, dest_path)
        else:
            # Cross-provider copy
            content = await source_fs.get_file(source_path)
            source_metadata = await source_fs.get_file_metadata(source_path)
            
            metadata = source_metadata.provider_metadata if source_metadata else {}
            return await dest_fs.put_file(dest_path, content, metadata)
    
    async def sync_files(self, source_path: str, dest_path: str,
                        source_provider: Optional[str] = None,
                        dest_provider: Optional[str] = None,
                        delete_extra: bool = False) -> Dict[str, Any]:
        """Sync files between providers or paths"""
        source_fs = self.get_provider(source_provider)
        dest_fs = self.get_provider(dest_provider)
        
        # Get file lists
        source_files = await source_fs.list_files(source_path, recursive=True)
        dest_files = await dest_fs.list_files(dest_path, recursive=True)
        
        # Create lookup maps
        source_map = {f.path: f for f in source_files if not f.is_directory}
        dest_map = {f.path: f for f in dest_files if not f.is_directory}
        
        sync_stats = {
            'copied': 0,
            'updated': 0,
            'deleted': 0,
            'skipped': 0,
            'errors': []
        }
        
        # Copy/update files
        for source_file_path, source_file in source_map.items():
            try:
                # Adjust destination path
                relative_path = source_file_path[len(source_path):].lstrip('/')
                dest_file_path = f"{dest_path.rstrip('/')}/{relative_path}"
                
                dest_file = dest_map.get(dest_file_path)
                
                if dest_file is None:
                    # File doesn't exist in destination - copy it
                    await self.copy_file(source_file_path, dest_file_path, 
                                       source_provider, dest_provider)
                    sync_stats['copied'] += 1
                    
                elif (source_file.modified and dest_file.modified and 
                      source_file.modified > dest_file.modified):
                    # Source is newer - update destination
                    await self.copy_file(source_file_path, dest_file_path, 
                                       source_provider, dest_provider)
                    sync_stats['updated'] += 1
                    
                else:
                    # Files are in sync
                    sync_stats['skipped'] += 1
                    
            except Exception as e:
                sync_stats['errors'].append({
                    'file': source_file_path,
                    'error': str(e)
                })
        
        # Delete extra files if requested
        if delete_extra:
            for dest_file_path in dest_map:
                # Check if this file exists in source
                relative_path = dest_file_path[len(dest_path):].lstrip('/')
                source_file_path = f"{source_path.rstrip('/')}/{relative_path}"
                
                if source_file_path not in source_map:
                    try:
                        await dest_fs.delete_file(dest_file_path)
                        sync_stats['deleted'] += 1
                    except Exception as e:
                        sync_stats['errors'].append({
                            'file': dest_file_path,
                            'error': str(e)
                        })
        
        return sync_stats
    
    async def search_files(self, pattern: str, path: str = "/", recursive: bool = True,
                          provider: Optional[str] = None) -> List[FileMetadata]:
        """Search files using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.search_files(pattern, path, recursive)
    
    async def batch_delete(self, paths: List[str], provider: Optional[str] = None) -> Dict[str, bool]:
        """Batch delete files using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.batch_delete(paths)
    
    async def batch_upload(self, files: Dict[str, bytes], 
                          metadata: Optional[Dict[str, str]] = None,
                          provider: Optional[str] = None) -> Dict[str, FileMetadata]:
        """Batch upload files using specified or default provider"""
        fs = self.get_provider(provider)
        return await fs.batch_upload(files, metadata)
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Clean up all providers
        for provider in self.providers.values():
            try:
                await provider.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass  # Ignore cleanup errors