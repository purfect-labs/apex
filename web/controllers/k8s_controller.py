"""
Kubernetes Controller - Business Logic Layer
Orchestrates K8s operations with environment safety and validation
"""

import asyncio
from .base_controller import BaseController
from typing import Dict, Any, Optional
from datetime import datetime
from ..utils.environment_mapper import validate_environment, get_gcp_project_for_env
from ..config_loader import get_config


class K8sController(BaseController):
    """Controller for Kubernetes operations - handles business logic and safety orchestration"""
    
    def __init__(self):
        super().__init__("k8s_controller")
        self.current_env = "dev"
        self.current_context = None
        self.config = get_config()
    
    async def authenticate(self, env: str = None, **kwargs) -> Dict[str, Any]:
        """Handle K8s cluster authentication with business logic validation"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "authentication")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_authenticate_start", {"env": env})
            
            # Get K8s operations provider
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "authentication")
                return {"success": False, "error": error_msg}
            
            # Execute authentication through provider
            result = await k8s_ops.authenticate(env=env)
            
            if result.get("success", True):
                self.current_env = env
                self.current_context = result.get("context")
                await self.log_action("k8s_authenticate_success", {
                    "env": env,
                    "project": result.get("project"),
                    "cluster": result.get("cluster"),
                    "context": result.get("context")
                })
            else:
                await self.handle_error(result.get("error", "K8s authentication failed"), "authentication")
            
            return result
            
        except Exception as e:
            error_msg = f"K8s authentication controller error: {str(e)}"
            await self.handle_error(error_msg, "authentication")
            return {"success": False, "error": error_msg}
    
    async def get_endpoints(self) -> Dict[str, Any]:
        """Auto-discover available K8s endpoints by testing real kubectl connectivity"""
        try:
            await self.log_action("discover_k8s_endpoints_start")
            
            endpoints = {
                "provider": "kubernetes",
                "controller": self.name,
                "available_endpoints": [],
                "kubectl_required": True,
                "discovered_at": datetime.now().isoformat()
            }
            
            # Test real kubectl connectivity using actual provider methods
            k8s_ops = self.get_provider("k8s_operations")
            if k8s_ops:
                try:
                    # Use real kubectl status method that exists
                    status_result = await k8s_ops.get_status()
                    if status_result.get("success", True) and status_result.get("kubectl_available", False):
                        # kubectl is working, expose all endpoints
                        endpoints["available_endpoints"].extend([
                            {
                                "endpoint": "/api/k8s/contexts",
                                "method": "GET",
                                "description": "List kubectl contexts (kubectl verified)",
                                "requires_auth": False,
                                "provider_verified": True
                            },
                            {
                                "endpoint": "/api/k8s/switch-context",
                                "method": "POST",
                                "description": "Switch kubectl context (kubectl verified)",
                                "requires_auth": True,
                                "parameters": ["context"],
                                "provider_verified": True
                            },
                            {
                                "endpoint": "/api/k8s/cluster-info",
                                "method": "GET",
                                "description": "Get cluster information (kubectl verified)",
                                "requires_auth": True,
                                "provider_verified": True
                            },
                            {
                                "endpoint": "/api/k8s/pods",
                                "method": "GET",
                                "description": "List pods in namespace (kubectl verified)",
                                "requires_auth": True,
                                "parameters": ["env?", "namespace?"],
                                "provider_verified": True
                            },
                            {
                                "endpoint": "/api/k8s/services",
                                "method": "GET",
                                "description": "List services in namespace (kubectl verified)",
                                "requires_auth": True,
                                "parameters": ["env?", "namespace?"],
                                "provider_verified": True
                            },
                            {
                                "endpoint": "/api/k8s/deployments",
                                "method": "GET",
                                "description": "List deployments in namespace (kubectl verified)",
                                "requires_auth": True,
                                "parameters": ["env?", "namespace?"],
                                "provider_verified": True
                            },
                            {
                                "endpoint": "/api/k8s/namespaces",
                                "method": "GET",
                                "description": "List all namespaces (kubectl verified)",
                                "requires_auth": True,
                                "parameters": ["env?"],
                                "provider_verified": True
                            }
                        ])
                    else:
                        # kubectl provider exists but not functional
                        endpoints["available_endpoints"].extend([
                            {
                                "endpoint": "/api/k8s/cluster-info",
                                "method": "GET",
                                "description": "Get cluster info (kubectl needs configuration)",
                                "requires_auth": True,
                                "provider_verified": False,
                                "provider_error": status_result.get("error", "kubectl not configured")
                            }
                        ])
                        
                except Exception as e:
                    # kubectl provider failed completely
                    await self.log_action("kubectl_discovery_failed", {"error": str(e)})
                    endpoints["available_endpoints"].append({
                        "endpoint": "/api/k8s/status",
                        "method": "GET",
                        "description": "Basic K8s controller status (no kubectl)",
                        "requires_auth": False,
                        "provider_verified": False,
                        "provider_error": str(e)
                    })
            
            # Test if authentication provider is available
            try:
                # Test real authentication by checking config
                k8s_config = self.config.get("k8s_contexts", [])
                if k8s_config and len(k8s_config) > 0:
                    endpoints["available_endpoints"].append({
                        "endpoint": "/api/k8s/authenticate",
                        "method": "POST",
                        "description": "Authenticate with K8s cluster (config verified)",
                        "requires_auth": True,
                        "parameters": ["env", "context?"],
                        "available_contexts": k8s_config,
                        "provider_verified": True
                    })
            except Exception as e:
                await self.log_action("k8s_auth_discovery_failed", {"error": str(e)})
            
            # Test raw kubectl execution capability using real controller methods
            try:
                # Check if we have a real kubectl execute method in controller
                if hasattr(self, 'execute_raw_kubectl'):
                    endpoints["available_endpoints"].append({
                        "endpoint": "/api/k8s/kubectl",
                        "method": "POST",
                        "description": "Execute raw kubectl commands (real controller method verified)",
                        "requires_auth": True,
                        "parameters": ["command", "env?", "namespace?"],
                        "provider_verified": True,
                        "warning": "Raw command execution - use with caution"
                    })
            except Exception as e:
                await self.log_action("kubectl_raw_discovery_failed", {"error": str(e)})
            
            endpoints["total_endpoints"] = len(endpoints["available_endpoints"])
            endpoints["verified_endpoints"] = len([ep for ep in endpoints["available_endpoints"] if ep.get("provider_verified", False)])
            endpoints["kubectl_functional"] = endpoints["verified_endpoints"] > 3  # More than basic endpoints means kubectl works
            
            await self.log_action("discover_k8s_endpoints_success", {
                "endpoint_count": endpoints["total_endpoints"],
                "verified_count": endpoints["verified_endpoints"],
                "kubectl_functional": endpoints["kubectl_functional"]
            })
            
            return {"success": True, "endpoints": endpoints}
            
        except Exception as e:
            error_msg = f"K8s endpoint discovery error: {str(e)}"
            await self.handle_error(error_msg, "endpoint_discovery")
            return {"success": False, "error": error_msg}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive K8s status"""
        try:
            status = {
                "controller": self.name,
                "current_env": self.current_env,
                "current_context": self.current_context
            }
            
            # Get cluster status
            k8s_ops = self.get_provider("k8s_operations")
            if k8s_ops:
                cluster_status = await k8s_ops.get_status()
                status["cluster"] = cluster_status
            
            return status
            
        except Exception as e:
            await self.handle_error(f"K8s status check error: {str(e)}", "status")
            return {"error": str(e)}
    
    async def get_pods(self, env: str = None, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Get pods in namespace with environment safety"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "get_pods")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_get_pods_start", {"env": env, "namespace": namespace})
            
            # Get K8s operations provider
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "get_pods")
                return {"success": False, "error": error_msg}
            
            # Execute with context safety
            result = await k8s_ops.get_pods(env=env, namespace=namespace, **kwargs)
            
            if result.get("success", True):
                # Parse and enhance pod data if JSON returned
                if 'stdout' in result and result['stdout']:
                    try:
                        import json
                        pod_data = json.loads(result['stdout'])
                        result['pods'] = pod_data.get('items', [])
                        result['pod_count'] = len(result['pods'])
                    except json.JSONDecodeError:
                        # Keep raw output if not JSON
                        pass
                
                await self.log_action("k8s_get_pods_success", {
                    "env": env, 
                    "namespace": namespace,
                    "pod_count": result.get("pod_count", 0)
                })
            else:
                await self.handle_error(result.get("error", "Failed to get pods"), "get_pods")
            
            return result
            
        except Exception as e:
            error_msg = f"K8s get pods controller error: {str(e)}"
            await self.handle_error(error_msg, "get_pods")
            return {"success": False, "error": error_msg}
    
    async def get_services(self, env: str = None, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Get services in namespace with environment safety"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "get_services")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_get_services_start", {"env": env, "namespace": namespace})
            
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "get_services")
                return {"success": False, "error": error_msg}
            
            result = await k8s_ops.get_services(env=env, namespace=namespace, **kwargs)
            
            if result.get("success", True):
                # Parse and enhance service data if JSON returned
                if 'stdout' in result and result['stdout']:
                    try:
                        import json
                        service_data = json.loads(result['stdout'])
                        result['services'] = service_data.get('items', [])
                        result['service_count'] = len(result['services'])
                    except json.JSONDecodeError:
                        pass
                
                await self.log_action("k8s_get_services_success", {
                    "env": env, 
                    "namespace": namespace,
                    "service_count": result.get("service_count", 0)
                })
            
            return result
            
        except Exception as e:
            error_msg = f"K8s get services controller error: {str(e)}"
            await self.handle_error(error_msg, "get_services")
            return {"success": False, "error": error_msg}
    
    async def get_deployments(self, env: str = None, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Get deployments in namespace with environment safety"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "get_deployments")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_get_deployments_start", {"env": env, "namespace": namespace})
            
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "get_deployments")
                return {"success": False, "error": error_msg}
            
            result = await k8s_ops.get_deployments(env=env, namespace=namespace, **kwargs)
            
            if result.get("success", True):
                # Parse and enhance deployment data if JSON returned
                if 'stdout' in result and result['stdout']:
                    try:
                        import json
                        deployment_data = json.loads(result['stdout'])
                        result['deployments'] = deployment_data.get('items', [])
                        result['deployment_count'] = len(result['deployments'])
                    except json.JSONDecodeError:
                        pass
                
                await self.log_action("k8s_get_deployments_success", {
                    "env": env, 
                    "namespace": namespace,
                    "deployment_count": result.get("deployment_count", 0)
                })
            
            return result
            
        except Exception as e:
            error_msg = f"K8s get deployments controller error: {str(e)}"
            await self.handle_error(error_msg, "get_deployments")
            return {"success": False, "error": error_msg}
    
    async def get_namespaces(self, env: str = None, **kwargs) -> Dict[str, Any]:
        """Get all namespaces with environment safety"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "get_namespaces")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_get_namespaces_start", {"env": env})
            
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "get_namespaces")
                return {"success": False, "error": error_msg}
            
            result = await k8s_ops.get_namespaces(env=env, **kwargs)
            
            if result.get("success", True):
                # Parse and enhance namespace data if JSON returned
                if 'stdout' in result and result['stdout']:
                    try:
                        import json
                        namespace_data = json.loads(result['stdout'])
                        result['namespaces'] = namespace_data.get('items', [])
                        result['namespace_count'] = len(result['namespaces'])
                    except json.JSONDecodeError:
                        pass
                
                await self.log_action("k8s_get_namespaces_success", {
                    "env": env,
                    "namespace_count": result.get("namespace_count", 0)
                })
            
            return result
            
        except Exception as e:
            error_msg = f"K8s get namespaces controller error: {str(e)}"
            await self.handle_error(error_msg, "get_namespaces")
            return {"success": False, "error": error_msg}
    
    async def describe_pod(self, pod_name: str, env: str = None, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Describe specific pod with environment safety"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "describe_pod")
                return {"success": False, "error": error_msg}
            
            if not pod_name:
                error_msg = "Pod name is required"
                await self.handle_error(error_msg, "describe_pod")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_describe_pod_start", {"env": env, "namespace": namespace, "pod_name": pod_name})
            
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "describe_pod")
                return {"success": False, "error": error_msg}
            
            result = await k8s_ops.describe_pod(env=env, pod_name=pod_name, namespace=namespace, **kwargs)
            
            if result.get("success", True):
                await self.log_action("k8s_describe_pod_success", {
                    "env": env, 
                    "namespace": namespace,
                    "pod_name": pod_name
                })
            
            return result
            
        except Exception as e:
            error_msg = f"K8s describe pod controller error: {str(e)}"
            await self.handle_error(error_msg, "describe_pod")
            return {"success": False, "error": error_msg}
    
    async def get_logs(self, pod_name: str, env: str = None, namespace: str = "default", tail: int = 100, **kwargs) -> Dict[str, Any]:
        """Get pod logs with environment safety"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "get_logs")
                return {"success": False, "error": error_msg}
            
            if not pod_name:
                error_msg = "Pod name is required"
                await self.handle_error(error_msg, "get_logs")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_get_logs_start", {
                "env": env, 
                "namespace": namespace, 
                "pod_name": pod_name, 
                "tail": tail
            })
            
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "get_logs")
                return {"success": False, "error": error_msg}
            
            result = await k8s_ops.get_logs(env=env, pod_name=pod_name, namespace=namespace, tail=tail, **kwargs)
            
            if result.get("success", True):
                await self.log_action("k8s_get_logs_success", {
                    "env": env, 
                    "namespace": namespace,
                    "pod_name": pod_name,
                    "tail": tail
                })
            
            return result
            
        except Exception as e:
            error_msg = f"K8s get logs controller error: {str(e)}"
            await self.handle_error(error_msg, "get_logs")
            return {"success": False, "error": error_msg}
    
    async def port_forward(self, resource: str, ports: str, env: str = None, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Start port forwarding with environment safety and background logging"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "port_forward")
                return {"success": False, "error": error_msg}
            
            if not resource or not ports:
                error_msg = "Resource and ports are required"
                await self.handle_error(error_msg, "port_forward")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_port_forward_start", {
                "env": env, 
                "namespace": namespace, 
                "resource": resource,
                "ports": ports
            })
            
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "port_forward")
                return {"success": False, "error": error_msg}
            
            # Use backgrounding and tmp logging as per rules
            result = await k8s_ops.port_forward(
                env=env, 
                resource=resource, 
                ports=ports, 
                namespace=namespace, 
                **kwargs
            )
            
            if result.get("success", True):
                await self.log_action("k8s_port_forward_success", {
                    "env": env, 
                    "namespace": namespace,
                    "resource": resource,
                    "ports": ports
                })
                
                # Inform user about log location
                await self.broadcast_message({
                    'type': 'command_output',
                    'data': {
                        'output': f'📝 Port forwarding logs available at: /tmp/apex-k8s-portforward-{env}-*.log',
                        'context': 'k8s_operations'
                    }
                })
            
            return result
            
        except Exception as e:
            error_msg = f"K8s port forward controller error: {str(e)}"
            await self.handle_error(error_msg, "port_forward")
            return {"success": False, "error": error_msg}
    
    async def execute_raw_kubectl(self, command: str, env: str = None, namespace: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute raw kubectl command with safety validation"""
        try:
            env = env or self.current_env
            
            if not validate_environment(env):
                error_msg = f"Invalid environment: {env}. Must be one of: dev, stage, prod"
                await self.handle_error(error_msg, "raw_kubectl")
                return {"success": False, "error": error_msg}
            
            if not command:
                error_msg = "Command is required"
                await self.handle_error(error_msg, "raw_kubectl")
                return {"success": False, "error": error_msg}
            
            await self.log_action("k8s_raw_kubectl_start", {
                "env": env, 
                "namespace": namespace, 
                "command": command
            })
            
            k8s_ops = self.get_provider("k8s_operations")
            if not k8s_ops:
                error_msg = "K8s operations provider not available"
                await self.handle_error(error_msg, "raw_kubectl")
                return {"success": False, "error": error_msg}
            
            result = await k8s_ops.execute_kubectl_command(
                command=command,
                env=env,
                namespace=namespace,
                **kwargs
            )
            
            if result.get("success", True):
                await self.log_action("k8s_raw_kubectl_success", {
                    "env": env, 
                    "namespace": namespace,
                    "command": command
                })
            
            return result
            
        except Exception as e:
            error_msg = f"K8s raw kubectl controller error: {str(e)}"
            await self.handle_error(error_msg, "raw_kubectl")
            return {"success": False, "error": error_msg}
    
    def set_environment(self, env: str):
        """Update current environment"""
        if validate_environment(env):
            self.current_env = env
            # Clear context cache when changing environments
            self.current_context = None
        else:
            raise ValueError(f"Invalid environment: {env}. Must be one of: dev, stage, prod")