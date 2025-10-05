"""
GCP Cloud Storage Filesystem Provider
Implements BaseFilesystem interface for Google Cloud Storage operations
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base_filesystem import BaseFilesystem, FileMetadata

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, Forbidden
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

class GCSFilesystem(BaseFilesystem):
    """Google Cloud Storage Filesystem Provider"""
    
    def __init__(self, bucket_name: str, project_id: Optional[str] = None,
                 credentials_path: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__("gcp_gcs", config)
        
        if not GCS_AVAILABLE:
            raise ImportError("google-cloud-storage is required for GCS filesystem operations. Install with: pip install google-cloud-storage")
        
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.credentials_path = credentials_path
        
        self.client = None
        self.bucket = None
    
    async def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Authenticate with Google Cloud Storage"""
        try:
            # Setup credentials
            client_kwargs = {}
            
            if self.project_id:
                client_kwargs['project'] = self.project_id
            
            if self.credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            
            # Create client
            self.client = storage.Client(**client_kwargs)
            
            # Get bucket reference and test access
            self.bucket = await asyncio.get_event_loop().run_in_executor(
                None, self.client.bucket, self.bucket_name
            )
            
            # Test bucket access by checking if it exists
            bucket_exists = await asyncio.get_event_loop().run_in_executor(
                None, self.bucket.exists
            )
            
            if not bucket_exists:
                return {
                    'success': False,
                    'error': f"GCS bucket '{self.bucket_name}' not found",
                    'provider': 'gcp_gcs',
                    'timestamp': datetime.now().isoformat()
                }
            
            self._authenticated = True
            
            return {
                'success': True,
                'provider': 'gcp_gcs',
                'bucket': self.bucket_name,
                'project': self.project_id or self.client.project,
                'authenticated': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except NotFound:
            return {
                'success': False,
                'error': f"GCS bucket '{self.bucket_name}' not found",
                'provider': 'gcp_gcs',
                'timestamp': datetime.now().isoformat()
            }
        except Forbidden as e:
            return {
                'success': False,
                'error': f"Access denied to GCS bucket '{self.bucket_name}': {str(e)}",
                'provider': 'gcp_gcs',
                'timestamp': datetime.now().isoformat()
            }
        except DefaultCredentialsError:
            return {
                'success': False,
                'error': 'GCP credentials not found. Please configure GCP credentials or set GOOGLE_APPLICATION_CREDENTIALS.',
                'provider': 'gcp_gcs',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"GCS authentication failed: {str(e)}",
                'provider': 'gcp_gcs',
                'timestamp': datetime.now().isoformat()
            }
    
    async def list_files(self, path: str = "/", recursive: bool = False, 
                        max_results: int = 1000) -> List[FileMetadata]:
        """List files in GCS bucket with optional path prefix"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            prefix = self.normalize_path(path)
            
            # Set up list parameters
            list_kwargs = {
                'max_results': max_results
            }
            
            if prefix:
                list_kwargs['prefix'] = prefix
            
            if not recursive and prefix and not prefix.endswith('/'):
                # For non-recursive listing, use delimiter to group by "folders"
                list_kwargs['delimiter'] = '/'
            
            # List blobs
            blobs = await asyncio.get_event_loop().run_in_executor(
                None, lambda: list(self.bucket.list_blobs(**list_kwargs))
            )
            
            files = []
            
            for blob in blobs:
                # Skip the prefix itself if it's a directory marker
                if blob.name == prefix:
                    continue
                
                files.append(FileMetadata(
                    path=blob.name,
                    size=blob.size or 0,
                    modified=blob.time_created,
                    etag=blob.etag,
                    provider_metadata={
                        'content_type': blob.content_type,
                        'storage_class': blob.storage_class,
                        'gcs_bucket': self.bucket_name,
                        'gcs_blob_name': blob.name,
                        'generation': blob.generation,
                        'metageneration': blob.metageneration
                    }
                ))
            
            # Handle common prefixes (directories) if delimiter was used
            if not recursive and hasattr(self.bucket, '_client'):
                # Get prefixes (this requires a more complex approach with GCS)
                # For now, we'll detect directories by looking for objects with trailing slashes
                directory_prefixes = set()
                for blob in blobs:
                    if '/' in blob.name:
                        parts = blob.name.split('/')
                        if len(parts) > 1:
                            dir_prefix = '/'.join(parts[:-1]) + '/'
                            if dir_prefix.startswith(prefix) and dir_prefix not in directory_prefixes:
                                directory_prefixes.add(dir_prefix)
                                files.append(FileMetadata(
                                    path=dir_prefix,
                                    size=0,
                                    modified=None,
                                    provider_metadata={
                                        'gcs_bucket': self.bucket_name,
                                        'gcs_prefix': dir_prefix,
                                        'directory': True
                                    }
                                ))
            
            return files
            
        except Exception as e:
            raise Exception(f"Failed to list GCS objects: {e}")
    
    async def get_file(self, path: str) -> bytes:
        """Download file content from GCS"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            blob_name = self.normalize_path(path)
            blob = self.bucket.blob(blob_name)
            
            content = await asyncio.get_event_loop().run_in_executor(
                None, blob.download_as_bytes
            )
            
            return content
            
        except NotFound:
            raise FileNotFoundError(f"File not found: {path}")
        except Exception as e:
            raise Exception(f"Failed to download file from GCS: {e}")
    
    async def put_file(self, path: str, content: bytes, 
                      metadata: Optional[Dict[str, str]] = None) -> FileMetadata:
        """Upload file content to GCS"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            blob_name = self.normalize_path(path)
            blob = self.bucket.blob(blob_name)
            
            if metadata:
                blob.metadata = metadata
            
            await asyncio.get_event_loop().run_in_executor(
                None, blob.upload_from_string, content
            )
            
            # Reload blob to get updated metadata
            await asyncio.get_event_loop().run_in_executor(
                None, blob.reload
            )
            
            return FileMetadata(
                path=blob_name,
                size=blob.size or len(content),
                modified=blob.time_created,
                etag=blob.etag,
                provider_metadata={
                    'content_type': blob.content_type,
                    'storage_class': blob.storage_class,
                    'gcs_bucket': self.bucket_name,
                    'gcs_blob_name': blob_name,
                    'generation': blob.generation,
                    'metageneration': blob.metageneration
                }
            )
            
        except Exception as e:
            raise Exception(f"Failed to upload file to GCS: {e}")
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from GCS"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            blob_name = self.normalize_path(path)
            blob = self.bucket.blob(blob_name)
            
            await asyncio.get_event_loop().run_in_executor(
                None, blob.delete
            )
            
            return True
            
        except NotFound:
            return False  # File already doesn't exist
        except Exception as e:
            raise Exception(f"Failed to delete file from GCS: {e}")
    
    async def file_exists(self, path: str) -> bool:
        """Check if file exists in GCS"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            blob_name = self.normalize_path(path)
            blob = self.bucket.blob(blob_name)
            
            exists = await asyncio.get_event_loop().run_in_executor(
                None, blob.exists
            )
            
            return exists
            
        except Exception as e:
            raise Exception(f"Failed to check file existence in GCS: {e}")
    
    async def get_file_metadata(self, path: str) -> Optional[FileMetadata]:
        """Get file metadata from GCS without downloading content"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            blob_name = self.normalize_path(path)
            blob = self.bucket.blob(blob_name)
            
            # Check if blob exists first
            exists = await asyncio.get_event_loop().run_in_executor(
                None, blob.exists
            )
            
            if not exists:
                return None
            
            # Reload to get fresh metadata
            await asyncio.get_event_loop().run_in_executor(
                None, blob.reload
            )
            
            return FileMetadata(
                path=blob_name,
                size=blob.size or 0,
                modified=blob.time_created,
                etag=blob.etag,
                provider_metadata={
                    'content_type': blob.content_type,
                    'storage_class': blob.storage_class,
                    'metadata': blob.metadata or {},
                    'gcs_bucket': self.bucket_name,
                    'gcs_blob_name': blob_name,
                    'generation': blob.generation,
                    'metageneration': blob.metageneration
                }
            )
            
        except NotFound:
            return None
        except Exception as e:
            raise Exception(f"Failed to get file metadata from GCS: {e}")
    
    async def get_file_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        """Generate signed URL for GCS object"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            blob_name = self.normalize_path(path)
            blob = self.bucket.blob(blob_name)
            
            from datetime import timedelta
            
            url = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: blob.generate_signed_url(
                    expiration=timedelta(seconds=expires_in),
                    method='GET'
                )
            )
            
            return url
            
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {e}")
    
    async def stream_file(self, path: str, chunk_size: int = 8192):
        """Stream file from GCS in chunks"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            blob_name = self.normalize_path(path)
            blob = self.bucket.blob(blob_name)
            
            # Download in chunks
            with blob.open("rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    
        except NotFound:
            raise FileNotFoundError(f"File not found: {path}")
        except Exception as e:
            raise Exception(f"Failed to stream file from GCS: {e}")
    
    async def batch_delete(self, paths: List[str]) -> Dict[str, bool]:
        """Delete multiple files from GCS in batch"""
        if not self._authenticated:
            await self.authenticate()
        
        if not paths:
            return {}
        
        try:
            results = {}
            
            # GCS doesn't have native batch delete, so we do concurrent deletes
            async def delete_single(path: str) -> tuple[str, bool]:
                try:
                    success = await self.delete_file(path)
                    return path, success
                except Exception:
                    return path, False
            
            # Execute deletions concurrently
            tasks = [delete_single(path) for path in paths]
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in completed_results:
                if isinstance(result, Exception):
                    # Handle any exceptions during concurrent execution
                    continue
                path, success = result
                results[path] = success
            
            return results
            
        except Exception as e:
            # If batch operations fail, fall back to sequential deletes
            return await super().batch_delete(paths)
    
    async def batch_upload(self, files: Dict[str, bytes], 
                          metadata: Optional[Dict[str, str]] = None) -> Dict[str, FileMetadata]:
        """Upload multiple files to GCS concurrently"""
        if not self._authenticated:
            await self.authenticate()
        
        if not files:
            return {}
        
        try:
            results = {}
            
            async def upload_single(path: str, content: bytes) -> tuple[str, Optional[FileMetadata]]:
                try:
                    file_metadata = await self.put_file(path, content, metadata)
                    return path, file_metadata
                except Exception:
                    return path, None
            
            # Execute uploads concurrently
            tasks = [upload_single(path, content) for path, content in files.items()]
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in completed_results:
                if isinstance(result, Exception):
                    # Handle any exceptions during concurrent execution
                    continue
                path, file_metadata = result
                results[path] = file_metadata
            
            return results
            
        except Exception as e:
            # If batch operations fail, fall back to sequential uploads
            return await super().batch_upload(files, metadata)