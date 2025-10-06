"""
Kubernetes Resource Management Routes
/api/k8s/* endpoints for comprehensive K8s operations
"""

from fastapi import BackgroundTasks
from typing import Optional


def setup_k8s_resource_routes(app, controller_registry):
    """Setup comprehensive K8s resource management routes"""
    
    # Context Management
    @app.get("/api/k8s/contexts")
    async def k8s_list_contexts():
        """List available kubectl contexts"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.list_contexts()
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/k8s/context/switch")
    async def k8s_switch_context(request: dict):
        """Switch kubectl context"""
        try:
            context = request.get('context')
            if not context:
                return {"success": False, "error": "Context parameter required"}
                
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.switch_context(context)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/status")
    async def k8s_get_status():
        """Get comprehensive K8s status"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_status()
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/endpoints")
    async def k8s_get_endpoints():
        """Get available K8s endpoints with real-time discovery"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller and hasattr(k8s_controller, 'get_endpoints'):
                return await k8s_controller.get_endpoints()
            else:
                return {"success": False, "error": "K8s controller not available or endpoint discovery not implemented"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Universal Resource Operations
    @app.get("/api/k8s/resources/{resource_type}")
    async def k8s_get_resources(resource_type: str, env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Universal GET endpoint for any K8s resource type"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_resources(resource_type, env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Specific Resource Endpoints  
    @app.get("/api/k8s/pods")
    async def k8s_get_pods(env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Get pods in namespace"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_pods(env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/services")
    async def k8s_get_services(env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Get services in namespace"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_services(env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/deployments")
    async def k8s_get_deployments(env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Get deployments in namespace"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_deployments(env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/namespaces")
    async def k8s_get_namespaces(env: Optional[str] = "dev"):
        """Get all namespaces"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_namespaces(env)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/configmaps")
    async def k8s_get_configmaps(env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Get configmaps in namespace"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_configmaps(env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/secrets")
    async def k8s_get_secrets(env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Get secrets in namespace"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_secrets(env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/k8s/ingresses")
    async def k8s_get_ingresses(env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Get ingresses in namespace"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_ingresses(env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Resource Operations
    @app.delete("/api/k8s/resources/{resource_type}/{resource_name}")
    async def k8s_delete_resource(resource_type: str, resource_name: str, env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Delete a specific K8s resource"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.delete_resource(resource_type, resource_name, env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.patch("/api/k8s/resources/{resource_type}/{resource_name}")
    async def k8s_patch_resource(resource_type: str, resource_name: str, request: dict, env: Optional[str] = "dev", namespace: Optional[str] = "default"):
        """Patch a K8s resource with JSON patch data"""
        try:
            patch_data = request.get('patch', {})
            if not patch_data:
                return {"success": False, "error": "Patch data required"}
                
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.patch_resource(resource_type, resource_name, patch_data, env, namespace)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Pod Operations
    @app.get("/api/k8s/pods/{pod_name}/logs")
    async def k8s_get_pod_logs(pod_name: str, env: Optional[str] = "dev", namespace: Optional[str] = "default", tail: Optional[int] = 100):
        """Get logs from a pod"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                return await k8s_controller.get_pod_logs(pod_name, env, namespace, tail)
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Raw kubectl execution
    @app.post("/api/k8s/kubectl")
    async def k8s_execute_kubectl(request: dict, background_tasks: BackgroundTasks):
        """Execute raw kubectl command with safety validation"""
        try:
            command = request.get('command')
            env = request.get('env', 'dev')
            namespace = request.get('namespace')
            
            if not command:
                return {"success": False, "error": "Command parameter required"}
                
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                # Execute in background for long-running commands
                background_tasks.add_task(k8s_controller.execute_raw_kubectl, command, env, namespace)
                return {
                    "success": True, 
                    "message": f"Executing kubectl command in {env}: {command[:50]}...",
                    "env": env,
                    "namespace": namespace
                }
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Authentication
    @app.post("/api/k8s/auth/{env}")
    async def k8s_authenticate_env(env: str, background_tasks: BackgroundTasks):
        """Authenticate kubectl with specific environment cluster"""
        try:
            k8s_controller = controller_registry.get_controller("k8s")
            if k8s_controller:
                background_tasks.add_task(k8s_controller.authenticate, env=env)
                return {"success": True, "message": f"K8s authentication initiated for {env} with context validation"}
            else:
                return {"success": False, "error": "K8s controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}