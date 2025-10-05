"""
Base Filesystem Provider Abstract Class
Provides unified interface for provider-native file systems (AWS S3, GCP GCS, Azure Blob, etc.)
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, BinaryIO, IO
from pathlib import Path

class FileMetadata:
    """Unified file metadata structure"""
    def __init__(self, path: str, size: int = 0, modified: Optional[datetime] = None,
                 etag: Optional[str] = None, provider_metadata: Optional[Dict] = None):
        self.path = path
        self.size = size
        self.modified = modified or datetime.now()
        self.etag = etag
        self.provider_metadata = provider_metadata or {}
        self.is_directory = path.endswith('/')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'size': self.size,
            'modified': self.modified.isoformat() if self.modified else None,
            'etag': self.etag,
            'is_directory': self.is_directory,
            'provider_metadata': self.provider_metadata
        }

class BaseFilesystem(ABC):
    """Base class for all filesystem providers"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.client = None
        self._authenticated = False
    
    @abstractmethod
    async def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Authenticate with the filesystem service"""
        pass
    
    @abstractmethod
    async def list_files(self, path: str = "/", recursive: bool = False, 
                        max_results: int = 1000) -> List[FileMetadata]:
        """List files and directories at the given path"""
        pass
    
    @abstractmethod
    async def get_file(self, path: str) -> bytes:
        """Get file contents as bytes"""
        pass
    
    @abstractmethod
    async def put_file(self, path: str, content: bytes, 
                      metadata: Optional[Dict[str, str]] = None) -> FileMetadata:
        """Upload file content to the given path"""
        pass
    
    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Delete file at the given path"""
        pass
    
    @abstractmethod
    async def file_exists(self, path: str) -> bool:
        """Check if file exists at the given path"""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, path: str) -> Optional[FileMetadata]:
        """Get file metadata without downloading content"""
        pass
    
    # Optional streaming support
    async def stream_file(self, path: str, chunk_size: int = 8192) -> Any:
        """Stream file contents in chunks (default implementation)"""
        content = await self.get_file(path)
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]
    
    async def put_file_stream(self, path: str, stream: Any, 
                             metadata: Optional[Dict[str, str]] = None) -> FileMetadata:
        """Upload file from stream (default implementation)"""
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        content = b''.join(chunks)
        return await self.put_file(path, content, metadata)
    
    # Directory operations
    async def create_directory(self, path: str) -> bool:
        """Create directory (for filesystems that support directories)"""
        # Default implementation for object stores - create empty marker object
        if not path.endswith('/'):
            path += '/'
        try:
            await self.put_file(path, b'', {'directory': 'true'})
            return True
        except Exception:
            return False
    
    async def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """Delete directory and optionally its contents"""
        if not path.endswith('/'):
            path += '/'
        
        if recursive:
            # List and delete all files in directory
            files = await self.list_files(path, recursive=True)
            for file_meta in files:
                if not file_meta.is_directory:
                    await self.delete_file(file_meta.path)
        
        # Delete the directory marker
        return await self.delete_file(path)
    
    # Utility methods
    def normalize_path(self, path: str) -> str:
        """Normalize path for the specific filesystem"""
        # Remove leading slash for object stores
        return path.lstrip('/') if path.startswith('/') else path
    
    def get_parent_path(self, path: str) -> str:
        """Get parent directory path"""
        normalized = self.normalize_path(path)
        if '/' not in normalized:
            return ''
        return '/'.join(normalized.split('/')[:-1]) + '/'
    
    def get_filename(self, path: str) -> str:
        """Extract filename from path"""
        normalized = self.normalize_path(path)
        if normalized.endswith('/'):
            normalized = normalized[:-1]
        return normalized.split('/')[-1]
    
    async def copy_file(self, source_path: str, dest_path: str) -> FileMetadata:
        """Copy file from source to destination"""
        content = await self.get_file(source_path)
        source_metadata = await self.get_file_metadata(source_path)
        
        metadata = source_metadata.provider_metadata if source_metadata else {}
        return await self.put_file(dest_path, content, metadata)
    
    async def move_file(self, source_path: str, dest_path: str) -> FileMetadata:
        """Move file from source to destination"""
        result = await self.copy_file(source_path, dest_path)
        await self.delete_file(source_path)
        return result
    
    async def get_file_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        """Get a presigned URL for the file (if supported by provider)"""
        # Default implementation returns None - override in provider implementations
        return None
    
    # Batch operations
    async def batch_delete(self, paths: List[str]) -> Dict[str, bool]:
        """Delete multiple files in batch"""
        results = {}
        for path in paths:
            try:
                results[path] = await self.delete_file(path)
            except Exception as e:
                results[path] = False
        return results
    
    async def batch_upload(self, files: Dict[str, bytes], 
                          metadata: Optional[Dict[str, str]] = None) -> Dict[str, FileMetadata]:
        """Upload multiple files in batch"""
        results = {}
        for path, content in files.items():
            try:
                results[path] = await self.put_file(path, content, metadata)
            except Exception as e:
                results[path] = None
        return results
    
    # Search and filtering
    async def search_files(self, pattern: str, path: str = "/", 
                          recursive: bool = True) -> List[FileMetadata]:
        """Search for files matching pattern"""
        import fnmatch
        
        all_files = await self.list_files(path, recursive=recursive)
        matching_files = []
        
        for file_meta in all_files:
            filename = self.get_filename(file_meta.path)
            if fnmatch.fnmatch(filename, pattern):
                matching_files.append(file_meta)
        
        return matching_files
    
    async def filter_files(self, path: str = "/", recursive: bool = True,
                          min_size: Optional[int] = None, max_size: Optional[int] = None,
                          modified_after: Optional[datetime] = None,
                          modified_before: Optional[datetime] = None) -> List[FileMetadata]:
        """Filter files by various criteria"""
        all_files = await self.list_files(path, recursive=recursive)
        filtered_files = []
        
        for file_meta in all_files:
            # Size filters
            if min_size is not None and file_meta.size < min_size:
                continue
            if max_size is not None and file_meta.size > max_size:
                continue
            
            # Date filters
            if modified_after is not None and file_meta.modified < modified_after:
                continue
            if modified_before is not None and file_meta.modified > modified_before:
                continue
            
            filtered_files.append(file_meta)
        
        return filtered_files
    
    # Status and health
    async def get_status(self) -> Dict[str, Any]:
        """Get filesystem status and health"""
        try:
            # Test basic connectivity
            test_files = await self.list_files("/", max_results=1)
            
            return {
                'authenticated': self._authenticated,
                'accessible': True,
                'provider': self.name,
                'test_successful': True,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'authenticated': self._authenticated,
                'accessible': False,
                'provider': self.name,
                'error': str(e),
                'test_successful': False,
                'timestamp': datetime.now().isoformat()
            }
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        if not self._authenticated:
            await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup if needed
        pass