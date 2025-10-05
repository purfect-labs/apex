"""
Filesystem Providers Package
Provider-native filesystem abstractions for APEX
"""

from .base_filesystem import BaseFilesystem, FileMetadata
from .filesystem_manager import FilesystemManager

# Import specific filesystem implementations
try:
    from .s3_filesystem import S3Filesystem
    S3_AVAILABLE = True
except ImportError:
    S3Filesystem = None
    S3_AVAILABLE = False

try:
    from .gcs_filesystem import GCSFilesystem
    GCS_AVAILABLE = True
except ImportError:
    GCSFilesystem = None
    GCS_AVAILABLE = False

__all__ = [
    'BaseFilesystem',
    'FileMetadata', 
    'FilesystemManager',
    'S3Filesystem',
    'GCSFilesystem',
    'S3_AVAILABLE',
    'GCS_AVAILABLE'
]

# Convenience function to create a filesystem manager with common configurations
async def create_filesystem_manager_from_config(config: dict) -> FilesystemManager:
    """
    Create and configure a filesystem manager from configuration
    
    Expected config structure:
    {
        "filesystems": {
            "aws_s3": {
                "name": "s3-storage",
                "bucket_name": "my-bucket",
                "region": "us-west-2",
                "aws_access_key_id": "...",
                "aws_secret_access_key": "...",
                "default": true
            },
            "gcp_gcs": {
                "name": "gcs-storage", 
                "bucket_name": "my-gcs-bucket",
                "project_id": "my-project",
                "credentials_path": "/path/to/credentials.json"
            }
        }
    }
    """
    manager = FilesystemManager()
    
    filesystems_config = config.get('filesystems', {})
    
    # Configure S3 filesystems
    if 'aws_s3' in filesystems_config and S3_AVAILABLE:
        s3_config = filesystems_config['aws_s3']
        
        await manager.create_and_register_s3(
            name=s3_config.get('name', 'aws_s3'),
            bucket_name=s3_config['bucket_name'],
            region=s3_config.get('region', 'us-west-2'),
            aws_access_key_id=s3_config.get('aws_access_key_id'),
            aws_secret_access_key=s3_config.get('aws_secret_access_key'),
            aws_session_token=s3_config.get('aws_session_token'),
            endpoint_url=s3_config.get('endpoint_url'),
            set_as_default=s3_config.get('default', False)
        )
    
    # Configure GCS filesystems
    if 'gcp_gcs' in filesystems_config and GCS_AVAILABLE:
        gcs_config = filesystems_config['gcp_gcs']
        
        await manager.create_and_register_gcs(
            name=gcs_config.get('name', 'gcp_gcs'),
            bucket_name=gcs_config['bucket_name'],
            project_id=gcs_config.get('project_id'),
            credentials_path=gcs_config.get('credentials_path'),
            set_as_default=gcs_config.get('default', False)
        )
    
    return manager