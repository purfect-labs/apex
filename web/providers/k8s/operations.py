"""
Kubernetes Operations Provider
Handles kubectl operations with MANDATORY context validation and switching
SAFETY FIRST - Always validates correct context before every command
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional
from ..base_provider import BaseProvider
from ...config_loader import get_config
from ...utils.environment_mapper import get_gcp_project_for_env, validate_environment


class K8sOperations(BaseProvider):
    """Kubernetes Operations Provider with Context Safety"""
    
    def __init__(self):
        super().__init__("k8s_operations")
        self.config_loader = get_config()
        self._current_context_cache = None
        self._cache_timeout = 10  # Short cache for context checks
        self._last_context_check = 0
    
    async def authenticate(self, env: str = "dev", **kwargs) -> Dict[str, Any]:
        """Authenticate kubectl with specific environment cluster"""
        try:
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.broadcast_message({
                    'type': 'k8s_error',
                    'data': {'error': error_msg, 'context': 'authenticate'}
                })
                return {'success': False, 'error': error_msg}
            
            await self.broadcast_message({
                'type': 'k8s_auth_started',
                'data': {
                    'message': f'🔐 Authenticating kubectl with {env} cluster...',
                    'env': env
                }
            })
            
            # Get GCP project for environment
            try:
                project = get_gcp_project_for_env(env)
            except ValueError as e:
                await self.broadcast_message({
                    'type': 'k8s_error',
                    'data': {'error': str(e), 'context': 'authenticate'}
                })
                return {'success': False, 'error': str(e)}
            
            # Get cluster config from GCP configuration
            gcp_config = self.config_loader.get_gcp_config()
            project_config = gcp_config.get('projects', {}).get(env, {})
            
            cluster = project_config.get('cluster')
            region = project_config.get('region')
            
            if not cluster or not region:
                error_msg = f"Missing cluster or region config for {env}"
                await self.broadcast_message({
                    'type': 'k8s_error',
                    'data': {'error': error_msg, 'context': 'authenticate'}
                })
                return {'success': False, 'error': error_msg}
            
            # Authenticate kubectl with GKE cluster
            auth_command = f"gcloud container clusters get-credentials {cluster} --region={region} --project={project}"
            
            result = await self.execute_command(
                auth_command,
                env=self.get_env_vars(),
                stream_output=True
            )
            
            if result['success']:
                # Verify the context was set correctly
                context_check = await self._verify_context(env)
                if context_check['success']:
                    await self.broadcast_message({
                        'type': 'k8s_auth_success',
                        'data': {
                            'env': env,
                            'project': project,
                            'cluster': cluster,
                            'context': context_check['context'],
                            'message': f'✅ kubectl authenticated with {env} cluster'
                        }
                    })
                    
                    # Clear cache to force fresh context check
                    self._current_context_cache = None
                    
                    return {
                        'success': True,
                        'env': env,
                        'project': project,
                        'cluster': cluster,
                        'context': context_check['context']
                    }
                else:
                    error_msg = f"Authentication appeared successful but context verification failed: {context_check.get('error', 'Unknown error')}"
                    await self.broadcast_message({
                        'type': 'k8s_error',
                        'data': {'error': error_msg, 'context': 'authenticate'}
                    })
                    return {'success': False, 'error': error_msg}
            else:
                await self.broadcast_message({
                    'type': 'k8s_error',
                    'data': {
                        'error': result.get('stderr', result.get('error', 'Unknown error')),
                        'context': 'authenticate'
                    }
                })
                return result
                
        except Exception as e:
            error_msg = f'K8s authentication failed: {str(e)}'
            await self.broadcast_message({
                'type': 'k8s_error',
                'data': {'error': error_msg, 'context': 'authenticate'}
            })
            return {'success': False, 'error': error_msg}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get kubectl status and current context"""
        try:
            # Get current context
            context_result = await self.execute_command(
                'kubectl config current-context',
                env=self.get_env_vars(),
                stream_output=False
            )
            
            if not context_result['success']:
                return {
                    'connected': False,
                    'error': 'No kubectl context configured',
                    'timestamp': context_result.get('timestamp')
                }
            
            current_context = context_result['stdout'].strip()
            
            # Test cluster connectivity
            cluster_test = await self.execute_command(
                'kubectl cluster-info --request-timeout=5s',
                env=self.get_env_vars(),
                stream_output=False
            )
            
            if cluster_test['success']:
                # Get cluster version for additional info
                version_result = await self.execute_command(
                    'kubectl version --short --client=false',
                    env=self.get_env_vars(),
                    stream_output=False
                )
                
                return {
                    'connected': True,
                    'current_context': current_context,
                    'cluster_info': cluster_test['stdout'],
                    'version_info': version_result.get('stdout') if version_result['success'] else None,
                    'timestamp': context_result['timestamp']
                }
            else:
                return {
                    'connected': False,
                    'current_context': current_context,
                    'error': 'Could not reach cluster',
                    'cluster_error': cluster_test.get('stderr', 'Unknown error'),
                    'timestamp': context_result['timestamp']
                }
                
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'timestamp': None
            }
    
    async def execute_kubectl_command(self, command: str, env: str, namespace: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        SAFE kubectl command execution with MANDATORY context validation
        Always validates and switches to correct context before executing any command
        """
        try:
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                return {'success': False, 'error': error_msg}
            
            # STEP 1: Validate current context matches expected environment
            context_validation = await self._validate_and_switch_context(env)
            if not context_validation['success']:
                return context_validation
            
            # STEP 2: Build kubectl command with proper namespace
            kubectl_cmd = f"kubectl {command}"
            if namespace:
                kubectl_cmd += f" --namespace={namespace}"
            
            # STEP 3: Add safety timeout for potentially hanging commands
            kubectl_cmd = f"timeout 60s {kubectl_cmd}"
            
            await self.broadcast_message({
                'type': 'command_output',
                'data': {
                    'output': f'⚡ [SAFE] Executing kubectl command in {env}: {command}',
                    'context': 'k8s_operations'
                }
            })
            
            # STEP 4: Execute the command
            result = await self.execute_command(
                kubectl_cmd,
                env=self.get_env_vars(),
                stream_output=kwargs.get('stream_output', True)
            )
            
            # STEP 5: Add context info to result
            result['executed_in_env'] = env
            result['kubectl_context'] = context_validation['context']
            result['namespace'] = namespace
            
            return result
            
        except Exception as e:
            error_msg = f'Safe kubectl execution failed: {str(e)}'
            await self.broadcast_message({
                'type': 'k8s_error',
                'data': {'error': error_msg, 'context': 'execute_kubectl_command'}
            })
            return {'success': False, 'error': error_msg}
    
    async def get_pods(self, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Get pods in specific namespace with context safety"""
        return await self.execute_kubectl_command(
            f"get pods -o json",
            env=env,
            namespace=namespace,
            stream_output=kwargs.get('stream_output', False)
        )
    
    async def get_services(self, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Get services in specific namespace with context safety"""
        return await self.execute_kubectl_command(
            f"get services -o json",
            env=env,
            namespace=namespace,
            stream_output=kwargs.get('stream_output', False)
        )
    
    async def get_deployments(self, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Get deployments in specific namespace with context safety"""
        return await self.execute_kubectl_command(
            f"get deployments -o json",
            env=env,
            namespace=namespace,
            stream_output=kwargs.get('stream_output', False)
        )
    
    async def get_namespaces(self, env: str, **kwargs) -> Dict[str, Any]:
        """Get all namespaces with context safety"""
        return await self.execute_kubectl_command(
            "get namespaces -o json",
            env=env,
            stream_output=kwargs.get('stream_output', False)
        )
    
    async def describe_pod(self, env: str, pod_name: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Describe specific pod with context safety"""
        return await self.execute_kubectl_command(
            f"describe pod {pod_name}",
            env=env,
            namespace=namespace,
            stream_output=kwargs.get('stream_output', True)
        )
    
    async def get_logs(self, env: str, pod_name: str, namespace: str = "default", tail: int = 100, **kwargs) -> Dict[str, Any]:
        """Get pod logs with context safety"""
        return await self.execute_kubectl_command(
            f"logs {pod_name} --tail={tail}",
            env=env,
            namespace=namespace,
            stream_output=kwargs.get('stream_output', True)
        )
    
    async def port_forward(self, env: str, resource: str, ports: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Start port forwarding with context safety (runs in background)"""
        try:
            # Validate context first
            context_validation = await self._validate_and_switch_context(env)
            if not context_validation['success']:
                return context_validation
            
            await self.broadcast_message({
                'type': 'command_output',
                'data': {
                    'output': f'🔗 Starting port forward in {env}: {resource} -> {ports}',
                    'context': 'k8s_operations'
                }
            })
            
            # Port forwarding runs in background with nohup
            port_forward_cmd = f"nohup kubectl port-forward {resource} {ports} --namespace={namespace} > /tmp/apex-k8s-portforward-{env}-$(date +%s).log 2>&1 &"
            
            result = await self.execute_command(
                port_forward_cmd,
                env=self.get_env_vars(),
                stream_output=kwargs.get('stream_output', True)
            )
            
            result['executed_in_env'] = env
            result['resource'] = resource
            result['ports'] = ports
            result['namespace'] = namespace
            
            return result
            
        except Exception as e:
            error_msg = f'Port forwarding failed: {str(e)}'
            await self.broadcast_message({
                'type': 'k8s_error',
                'data': {'error': error_msg, 'context': 'port_forward'}
            })
            return {'success': False, 'error': error_msg}
    
    async def _validate_and_switch_context(self, env: str) -> Dict[str, Any]:
        """
        CRITICAL SAFETY FUNCTION
        Validates current kubectl context matches expected environment
        Switches context if necessary to prevent cross-environment operations
        """
        try:
            # Get expected context pattern for environment
            expected_context_pattern = await self._get_expected_context_pattern(env)
            if not expected_context_pattern['success']:
                return expected_context_pattern
            
            # Get current context
            current_result = await self.execute_command(
                'kubectl config current-context',
                env=self.get_env_vars(),
                stream_output=False
            )
            
            if not current_result['success']:
                error_msg = "No kubectl context is currently set"
                await self.broadcast_message({
                    'type': 'k8s_error',
                    'data': {'error': error_msg, 'context': 'context_validation'}
                })
                
                # Try to authenticate with correct environment
                auth_result = await self.authenticate(env=env)
                return auth_result
            
            current_context = current_result['stdout'].strip()
            expected_pattern = expected_context_pattern['pattern']
            
            # Check if current context matches expected pattern
            if expected_pattern not in current_context:
                await self.broadcast_message({
                    'type': 'command_output',
                    'data': {
                        'output': f'🚨 SAFETY: Current context "{current_context}" does not match {env} environment',
                        'context': 'k8s_operations'
                    }
                })
                
                await self.broadcast_message({
                    'type': 'command_output',
                    'data': {
                        'output': f'🔄 SAFETY: Switching to {env} cluster context...',
                        'context': 'k8s_operations'
                    }
                })
                
                # Authenticate with correct environment
                auth_result = await self.authenticate(env=env)
                if not auth_result['success']:
                    return auth_result
                
                return {
                    'success': True,
                    'context': auth_result['context'],
                    'switched': True,
                    'previous_context': current_context
                }
            else:
                # Context is correct
                return {
                    'success': True,
                    'context': current_context,
                    'switched': False
                }
                
        except Exception as e:
            error_msg = f'Context validation failed: {str(e)}'
            await self.broadcast_message({
                'type': 'k8s_error',
                'data': {'error': error_msg, 'context': 'context_validation'}
            })
            return {'success': False, 'error': error_msg}
    
    async def _get_expected_context_pattern(self, env: str) -> Dict[str, Any]:
        """Get expected kubectl context pattern for environment"""
        try:
            gcp_config = self.config_loader.get_gcp_config()
            project_config = gcp_config.get('projects', {}).get(env, {})
            
            cluster = project_config.get('cluster')
            project = get_gcp_project_for_env(env)
            
            if not cluster or not project:
                error_msg = f"Missing cluster or project config for {env}"
                return {'success': False, 'error': error_msg}
            
            # GKE context pattern: gke_{project}_{region}_{cluster}
            pattern = f"gke_{project}"
            
            return {
                'success': True,
                'pattern': pattern,
                'cluster': cluster,
                'project': project
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _verify_context(self, env: str) -> Dict[str, Any]:
        """Verify kubectl context matches expected environment"""
        try:
            context_result = await self.execute_command(
                'kubectl config current-context',
                env=self.get_env_vars(),
                stream_output=False
            )
            
            if not context_result['success']:
                return {'success': False, 'error': 'Could not get current context'}
            
            current_context = context_result['stdout'].strip()
            expected_pattern = await self._get_expected_context_pattern(env)
            
            if not expected_pattern['success']:
                return expected_pattern
            
            if expected_pattern['pattern'] in current_context:
                return {
                    'success': True,
                    'context': current_context,
                    'matches_env': env
                }
            else:
                return {
                    'success': False,
                    'error': f"Context '{current_context}' does not match {env} environment",
                    'context': current_context
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get K8s-specific environment variables"""
        return {
            'HOME': os.path.expanduser('~'),
            'KUBECONFIG': os.path.expanduser('~/.kube/config'),
            'CLOUDSDK_CORE_DISABLE_PROMPTS': '1'
        }