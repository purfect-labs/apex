"""
GCP Authentication Provider
Handles GCP authentication and project management
"""

import json
import os
from typing import Dict, Any, Optional, List
from ..base_provider import BaseProvider
from ...config_loader import get_config


class GCPAuth(BaseProvider):
    """GCP Authentication Provider"""
    
    def __init__(self):
        super().__init__("gcp_auth")
        self.config_loader = get_config()
        self._status_cache = None
        self._cache_time = 0
        self._cache_timeout = 300  # 5 minutes
    
    async def authenticate(self, project: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Authenticate with GCP (gcloud auth login)"""
        try:
            # Clear cache for fresh authentication attempt
            self._status_cache = None
            self._cache_time = 0
            
            # Always attempt authentication when manually triggered
            # This ensures GCP verification and project setup
            
            # Start authentication process
            await self.broadcast_message({
                'type': 'gcp_auth_started',
                'data': {
                    'message': '🔐 Starting GCP authentication...',
                    'timestamp': None
                }
            })
            
            await self.broadcast_message({
                'type': 'gcp_auth_output',
                'data': {
                    'output': '🌐 Your browser should open automatically for Google login...',
                    'timestamp': None
                }
            })
            
            # Execute gcloud auth login with streaming output
            result = await self.execute_command(
                'gcloud auth login --no-launch-browser',
                env=self.get_env_vars(),
                stream_output=True  # Show auth progress and links
            )
            
            if result['success']:
                # Verify authentication worked
                verify_result = await self.get_status()
                if verify_result.get('authenticated', False):
                    await self.broadcast_message({
                        'type': 'gcp_auth_success',
                        'data': {
                            'account': verify_result.get('active_account'),
                            'message': f'✅ GCP authentication successful!',
                            'timestamp': verify_result.get('timestamp')
                        }
                    })
                    
                    # Set project if specified
                    if project:
                        await self.set_project(project)
                    
                    return verify_result
                else:
                    error_msg = '❌ Login appeared to succeed but verification failed'
                    await self.broadcast_message({
                        'type': 'gcp_auth_error',
                        'data': {
                            'error': error_msg,
                            'timestamp': result.get('timestamp')
                        }
                    })
                    return {'success': False, 'error': error_msg}
            else:
                await self.broadcast_message({
                    'type': 'gcp_auth_error',
                    'data': {
                        'error': result.get('stderr', result.get('error', 'Unknown error')),
                        'timestamp': result.get('timestamp')
                    }
                })
                return result
                
        except Exception as e:
            error_msg = f'Failed to authenticate with GCP: {str(e)}'
            await self.broadcast_message({
                'type': 'gcp_auth_error',
                'data': {
                    'error': error_msg,
                    'timestamp': None
                }
            })
            return {'success': False, 'error': error_msg}
    
    async def set_project(self, project: str) -> Dict[str, Any]:
        """Set the active GCP project"""
        try:
            await self.broadcast_message({
                'type': 'gcp_auth_output',
                'data': {
                    'output': f'🔧 Setting GCP project to: {project}',
                    'timestamp': None
                }
            })
            
            result = await self.execute_command(
                f'gcloud config set project {project}',
                env=self.get_env_vars()
            )
            
            if result['success']:
                await self.broadcast_message({
                    'type': 'gcp_auth_output',
                    'data': {
                        'output': f'✅ GCP project set to: {project}',
                        'project': project,
                        'timestamp': result.get('timestamp')
                    }
                })
                return {'success': True, 'project': project}
            else:
                error_msg = f'Failed to set project: {result.get("stderr", "Unknown error")}'
                await self.broadcast_message({
                    'type': 'gcp_auth_error',
                    'data': {
                        'error': error_msg,
                        'timestamp': result.get('timestamp')
                    }
                })
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f'Failed to set GCP project: {str(e)}'
            await self.broadcast_message({
                'type': 'gcp_auth_error',
                'data': {
                    'error': error_msg,
                    'timestamp': None
                }
            })
            return {'success': False, 'error': error_msg}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get GCP authentication status with 5-minute caching"""
        import time
        
        # Check cache first
        if self._status_cache and time.time() - self._cache_time < self._cache_timeout:
            return self._status_cache
        
        try:
            # Check active account
            result = await self.execute_command(
                'gcloud auth list --filter="status:ACTIVE" --format="value(account)"',
                env=self.get_env_vars(),
                stream_output=False  # Don't spam terminal with status checks
            )
            
            if result['success'] and result['stdout'].strip():
                active_account = result['stdout'].strip()
                
                # Get current project
                project_result = await self.execute_command(
                    'gcloud config get-value project',
                    env=self.get_env_vars(),
                    stream_output=False  # Don't spam terminal with status checks
                )
                
                current_project = None
                if project_result['success'] and project_result['stdout'].strip():
                    current_project = project_result['stdout'].strip()
                
                # Get configured projects from config
                gcp_config = self.config_loader.get_gcp_config()
                configured_projects = gcp_config.get('projects', {})
                
                status_result = {
                    'authenticated': True,
                    'active_account': active_account,
                    'current_project': current_project,
                    'configured_projects': list(configured_projects.keys()),
                    'project_details': configured_projects,
                    'timestamp': result['timestamp']
                }
            else:
                status_result = {
                    'authenticated': False,
                    'error': 'No active GCP account found',
                    'timestamp': result.get('timestamp')
                }
            
            # Cache the result
            import time
            self._status_cache = status_result
            self._cache_time = time.time()
            return status_result
                
        except Exception as e:
            return {
                'authenticated': False,
                'error': str(e),
                'timestamp': None
            }
    
    async def list_projects(self) -> Dict[str, Any]:
        """List available GCP projects"""
        try:
            result = await self.execute_command(
                'gcloud projects list --format=json',
                env=self.get_env_vars()
            )
            
            if result['success']:
                projects = json.loads(result['stdout'])
                return {
                    'success': True,
                    'projects': projects,
                    'count': len(projects),
                    'timestamp': result['timestamp']
                }
            else:
                return {
                    'success': False,
                    'error': result.get('stderr', 'Failed to list projects'),
                    'timestamp': result.get('timestamp')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': None
            }
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get GCP-specific environment variables"""
        gcp_config = self.config_loader.get_gcp_config()
        
        env_vars = {
            'HOME': os.path.expanduser('~'),
            'CLOUDSDK_CORE_DISABLE_PROMPTS': '1',  # Disable interactive prompts
        }
        
        # Set default project and region if configured
        if 'default_region' in gcp_config:
            env_vars['CLOUDSDK_COMPUTE_REGION'] = gcp_config['default_region']
        
        if 'default_zone' in gcp_config:
            env_vars['CLOUDSDK_COMPUTE_ZONE'] = gcp_config['default_zone']
        
        return env_vars
    
    def get_project_config(self, env: str) -> Optional[Dict[str, Any]]:
        """Get project configuration for specific environment"""
        gcp_config = self.config_loader.get_gcp_config()
        return gcp_config.get('projects', {}).get(env)
