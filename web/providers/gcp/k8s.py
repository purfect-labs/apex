"""
GCP Kubernetes Provider
Handles GKE cluster operations and kubectl management
"""

import json
import os
from typing import Dict, Any, Optional
from ..base_provider import BaseProvider
from ...config_loader import get_config


class GCPK8s(BaseProvider):
    """GCP Kubernetes Provider"""
    
    def __init__(self):
        super().__init__("gcp_k8s")
        self.config_loader = get_config()
    
    async def authenticate(self, env: str = "dev", **kwargs) -> Dict[str, Any]:
        """Connect to GKE cluster for specified environment"""
        try:
            # Get cluster config for environment
            cluster_config = self.get_cluster_config(env)
            if not cluster_config:
                error_msg = f'No cluster configuration found for environment: {env}'
                await self.broadcast_message({
                    'type': 'gcp_k8s_error',
                    'data': {
                        'error': error_msg,
                        'env': env,
                        'timestamp': None
                    }
                })
                return {'success': False, 'error': error_msg}
            
            cluster_name = cluster_config.get('name')
            project = cluster_config.get('project')
            region = cluster_config.get('region')
            
            await self.broadcast_message({
                'type': 'gcp_k8s_started',
                'data': {
                    'message': f'🔗 Connecting to GKE cluster: {cluster_name}',
                    'env': env,
                    'cluster': cluster_name,
                    'project': project,
                    'timestamp': None
                }
            })
            
            # Get GKE cluster credentials
            result = await self.execute_command(
                f'gcloud container clusters get-credentials {cluster_name} --region={region} --project={project}',
                env=self.get_env_vars()
            )
            
            if result['success']:
                # Verify kubectl connection
                verify_result = await self.get_status()
                if verify_result.get('connected', False):
                    await self.broadcast_message({
                        'type': 'gcp_k8s_success',
                        'data': {
                            'env': env,
                            'cluster': cluster_name,
                            'context': verify_result.get('current_context'),
                            'message': f'✅ Connected to GKE cluster: {cluster_name}',
                            'timestamp': verify_result.get('timestamp')
                        }
                    })
                    return verify_result
                else:
                    error_msg = '❌ Cluster credentials obtained but kubectl verification failed'
                    await self.broadcast_message({
                        'type': 'gcp_k8s_error',
                        'data': {
                            'env': env,
                            'error': error_msg,
                            'timestamp': result.get('timestamp')
                        }
                    })
                    return {'success': False, 'error': error_msg}
            else:
                await self.broadcast_message({
                    'type': 'gcp_k8s_error',
                    'data': {
                        'env': env,
                        'error': result.get('stderr', result.get('error', 'Unknown error')),
                        'timestamp': result.get('timestamp')
                    }
                })
                return result
                
        except Exception as e:
            error_msg = f'Failed to connect to GKE cluster for {env}: {str(e)}'
            await self.broadcast_message({
                'type': 'gcp_k8s_error',
                'data': {
                    'env': env,
                    'error': error_msg,
                    'timestamp': None
                }
            })
            return {'success': False, 'error': error_msg}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current kubectl/GKE connection status"""
        try:
            # Check current context
            context_result = await self.execute_command(
                'kubectl config current-context',
                env=self.get_env_vars()
            )
            
            if context_result['success']:
                current_context = context_result['stdout'].strip()
                
                # Try to get cluster info to verify connection
                cluster_result = await self.execute_command(
                    'kubectl cluster-info --request-timeout=5s',
                    env=self.get_env_vars()
                )
                
                if cluster_result['success']:
                    return {
                        'connected': True,
                        'current_context': current_context,
                        'cluster_info': cluster_result['stdout'],
                        'timestamp': context_result['timestamp']
                    }
                else:
                    return {
                        'connected': False,
                        'current_context': current_context,
                        'error': 'Could not reach cluster',
                        'timestamp': context_result['timestamp']
                    }
            else:
                return {
                    'connected': False,
                    'error': 'No kubectl context configured',
                    'timestamp': context_result.get('timestamp')
                }
                
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'timestamp': None
            }
    
    async def list_clusters(self) -> Dict[str, Any]:
        """List available GKE clusters"""
        try:
            # Get current project
            project_result = await self.execute_command(
                'gcloud config get-value project',
                env=self.get_env_vars()
            )
            
            if not project_result['success']:
                return {
                    'success': False,
                    'error': 'No GCP project configured',
                    'timestamp': project_result.get('timestamp')
                }
            
            project = project_result['stdout'].strip()
            
            # List clusters
            result = await self.execute_command(
                f'gcloud container clusters list --project={project} --format=json',
                env=self.get_env_vars()
            )
            
            if result['success']:
                clusters = json.loads(result['stdout'])
                return {
                    'success': True,
                    'clusters': clusters,
                    'project': project,
                    'count': len(clusters),
                    'timestamp': result['timestamp']
                }
            else:
                return {
                    'success': False,
                    'error': result.get('stderr', 'Failed to list clusters'),
                    'timestamp': result.get('timestamp')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': None
            }
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get GCP K8s-specific environment variables"""
        gcp_config = self.config_loader.get_gcp_config()
        
        env_vars = {
            'HOME': os.path.expanduser('~'),
            'KUBECONFIG': os.path.expanduser('~/.kube/config'),
            'CLOUDSDK_CORE_DISABLE_PROMPTS': '1',  # Disable interactive prompts
        }
        
        # Set default project and region if configured
        if 'default_region' in gcp_config:
            env_vars['CLOUDSDK_COMPUTE_REGION'] = gcp_config['default_region']
        
        if 'default_zone' in gcp_config:
            env_vars['CLOUDSDK_COMPUTE_ZONE'] = gcp_config['default_zone']
        
        return env_vars
    
    def get_cluster_config(self, env: str) -> Optional[Dict[str, Any]]:
        """Get cluster configuration for specific environment"""
        gcp_config = self.config_loader.get_gcp_config()
        return gcp_config.get('clusters', {}).get(env)
