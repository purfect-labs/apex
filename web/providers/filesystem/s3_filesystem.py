"""
AWS S3 Filesystem Provider
Implements BaseFilesystem interface for AWS S3 operations
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base_filesystem import BaseFilesystem, FileMetadata

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    from botocore.config import Config
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

class S3Filesystem(BaseFilesystem):
    """AWS S3 Filesystem Provider"""
    
    def __init__(self, bucket_name: str, region: str = 'us-west-2', 
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_session_token: Optional[str] = None,
                 endpoint_url: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__("aws_s3", config)
        
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 filesystem operations. Install with: pip install boto3")
        
        self.bucket_name = bucket_name
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.endpoint_url = endpoint_url
        
        # Configure boto3 client
        self.boto_config = Config(
            region_name=region,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=50
        )
        
        self.client = None
        self.resource = None
    
    async def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Authenticate with AWS S3"""
        try:
            # Setup credentials
            session_kwargs = {}
            
            if self.aws_access_key_id and self.aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': self.aws_access_key_id,
                    'aws_secret_access_key': self.aws_secret_access_key
                })
                if self.aws_session_token:
                    session_kwargs['aws_session_token'] = self.aws_session_token
            
            # Create session and clients
            session = boto3.Session(**session_kwargs)
            
            client_kwargs = {
                'config': self.boto_config,
                'region_name': self.region
            }
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            
            self.client = session.client('s3', **client_kwargs)
            self.resource = session.resource('s3', **client_kwargs)
            
            # Test connection by checking if bucket exists and is accessible
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.head_bucket, {'Bucket': self.bucket_name}
            )
            
            self._authenticated = True
            
            return {
                'success': True,
                'provider': 'aws_s3',
                'bucket': self.bucket_name,
                'region': self.region,
                'authenticated': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                error_msg = f"S3 bucket '{self.bucket_name}' not found"
            elif error_code == '403':
                error_msg = f"Access denied to S3 bucket '{self.bucket_name}'"
            else:
                error_msg = f"S3 error ({error_code}): {e.response['Error']['Message']}"
            
            return {
                'success': False,
                'error': error_msg,
                'error_code': error_code,
                'provider': 'aws_s3',
                'timestamp': datetime.now().isoformat()
            }
        except NoCredentialsError:
            return {
                'success': False,
                'error': 'AWS credentials not found. Please configure AWS credentials.',
                'provider': 'aws_s3',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"S3 authentication failed: {str(e)}",
                'provider': 'aws_s3',
                'timestamp': datetime.now().isoformat()
            }
    
    async def list_files(self, path: str = "/", recursive: bool = False, 
                        max_results: int = 1000) -> List[FileMetadata]:
        """List files in S3 bucket with optional path prefix"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            prefix = self.normalize_path(path)
            
            kwargs = {
                'Bucket': self.bucket_name,
                'MaxKeys': max_results
            }
            
            if prefix:
                kwargs['Prefix'] = prefix
            
            if not recursive and prefix and not prefix.endswith('/'):
                # For non-recursive listing, add delimiter to group by "folders"
                kwargs['Delimiter'] = '/'
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.list_objects_v2, kwargs
            )
            
            files = []
            
            # Process objects (files)
            for obj in response.get('Contents', []):
                # Skip the prefix itself if it's a directory marker
                if obj['Key'] == prefix:
                    continue
                
                files.append(FileMetadata(
                    path=obj['Key'],
                    size=obj['Size'],
                    modified=obj['LastModified'],
                    etag=obj['ETag'].strip('"'),
                    provider_metadata={
                        'storage_class': obj.get('StorageClass', 'STANDARD'),
                        's3_bucket': self.bucket_name,
                        's3_key': obj['Key']
                    }
                ))
            
            # Process common prefixes (directories) if delimiter was used
            for prefix_info in response.get('CommonPrefixes', []):
                files.append(FileMetadata(
                    path=prefix_info['Prefix'],
                    size=0,
                    modified=None,
                    provider_metadata={
                        's3_bucket': self.bucket_name,
                        's3_prefix': prefix_info['Prefix'],
                        'directory': True
                    }
                ))
            
            return files
            
        except ClientError as e:
            raise Exception(f"Failed to list S3 objects: {e}")
    
    async def get_file(self, path: str) -> bytes:
        """Download file content from S3"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            key = self.normalize_path(path)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_object, {'Bucket': self.bucket_name, 'Key': key}
            )
            
            content = response['Body'].read()
            return content
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {path}")
            else:
                raise Exception(f"Failed to download file from S3: {e}")
    
    async def put_file(self, path: str, content: bytes, 
                      metadata: Optional[Dict[str, str]] = None) -> FileMetadata:
        """Upload file content to S3"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            key = self.normalize_path(path)
            
            kwargs = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Body': content
            }
            
            if metadata:
                kwargs['Metadata'] = metadata
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.put_object, kwargs
            )
            
            return FileMetadata(
                path=key,
                size=len(content),
                modified=datetime.now(),
                etag=response['ETag'].strip('"'),
                provider_metadata={
                    's3_bucket': self.bucket_name,
                    's3_key': key,
                    'version_id': response.get('VersionId')
                }
            )
            
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {e}")
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from S3"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            key = self.normalize_path(path)
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.delete_object, 
                {'Bucket': self.bucket_name, 'Key': key}
            )
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return False  # File already doesn't exist
            else:
                raise Exception(f"Failed to delete file from S3: {e}")
    
    async def file_exists(self, path: str) -> bool:
        """Check if file exists in S3"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            key = self.normalize_path(path)
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.head_object, 
                {'Bucket': self.bucket_name, 'Key': key}
            )
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise Exception(f"Failed to check file existence in S3: {e}")
    
    async def get_file_metadata(self, path: str) -> Optional[FileMetadata]:
        """Get file metadata from S3 without downloading content"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            key = self.normalize_path(path)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.head_object, 
                {'Bucket': self.bucket_name, 'Key': key}
            )
            
            return FileMetadata(
                path=key,
                size=response['ContentLength'],
                modified=response['LastModified'],
                etag=response['ETag'].strip('"'),
                provider_metadata={
                    'content_type': response.get('ContentType'),
                    'storage_class': response.get('StorageClass', 'STANDARD'),
                    'metadata': response.get('Metadata', {}),
                    's3_bucket': self.bucket_name,
                    's3_key': key,
                    'version_id': response.get('VersionId')
                }
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            else:
                raise Exception(f"Failed to get file metadata from S3: {e}")
    
    async def get_file_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        """Generate presigned URL for S3 object"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            key = self.normalize_path(path)
            
            url = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': key},
                    ExpiresIn=expires_in
                )
            )
            
            return url
            
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {e}")
    
    async def stream_file(self, path: str, chunk_size: int = 8192):
        """Stream file from S3 in chunks"""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            key = self.normalize_path(path)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_object, 
                {'Bucket': self.bucket_name, 'Key': key}
            )
            
            body = response['Body']
            
            while True:
                chunk = body.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {path}")
            else:
                raise Exception(f"Failed to stream file from S3: {e}")
        finally:
            if 'body' in locals():
                body.close()
    
    async def batch_delete(self, paths: List[str]) -> Dict[str, bool]:
        """Delete multiple files from S3 in batch"""
        if not self._authenticated:
            await self.authenticate()
        
        if not paths:
            return {}
        
        try:
            # S3 batch delete supports up to 1000 objects
            batch_size = 1000
            results = {}
            
            for i in range(0, len(paths), batch_size):
                batch_paths = paths[i:i + batch_size]
                
                delete_objects = {
                    'Objects': [{'Key': self.normalize_path(path)} for path in batch_paths]
                }
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.client.delete_objects,
                    {'Bucket': self.bucket_name, 'Delete': delete_objects}
                )
                
                # Mark successful deletions
                for deleted in response.get('Deleted', []):
                    # Find original path for this key
                    for path in batch_paths:
                        if self.normalize_path(path) == deleted['Key']:
                            results[path] = True
                            break
                
                # Mark failed deletions
                for error in response.get('Errors', []):
                    # Find original path for this key
                    for path in batch_paths:
                        if self.normalize_path(path) == error['Key']:
                            results[path] = False
                            break
            
            return results
            
        except ClientError as e:
            # If batch delete fails, fall back to individual deletes
            return await super().batch_delete(paths)