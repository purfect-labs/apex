"""
Controller Registry - Manages all controllers and provides centralized access
"""

from typing import Dict, Any, Optional, Type
from .base_controller import BaseController
from .aws_controller import AWSController
from .gcp_controller import GCPController
from .k8s_controller import K8sController
from .license_controller import LicenseController


class ControllerRegistry:
    """Registry for managing all controllers"""
    
    def __init__(self):
        self._controllers: Dict[str, BaseController] = {}
        self._provider_registry = None
        self._websocket_manager = None
        
        # Initialize default controllers
        self._init_controllers()
    
    def _init_controllers(self):
        """Initialize all available controllers"""
        # AWS Controller
        self._controllers["aws"] = AWSController()
        
        # GCP Controller  
        self._controllers["gcp"] = GCPController()
        
        # K8s Controller
        self._controllers["k8s"] = K8sController()
        
        # License Controller
        self._controllers["license"] = LicenseController()
    
    def set_provider_registry(self, provider_registry):
        """Set the provider registry for all controllers"""
        self._provider_registry = provider_registry
        for controller in self._controllers.values():
            controller.set_provider_registry(provider_registry)
    
    def set_websocket_manager(self, websocket_manager):
        """Set the WebSocket manager for all controllers"""
        self._websocket_manager = websocket_manager
        for controller in self._controllers.values():
            controller.set_websocket_manager(websocket_manager)
    
    def get_controller(self, name: str) -> Optional[BaseController]:
        """Get a controller by name"""
        return self._controllers.get(name)
    
    def get_aws_controller(self) -> AWSController:
        """Get the AWS controller"""
        return self._controllers.get("aws")
    
    def get_gcp_controller(self) -> GCPController:
        """Get the GCP controller"""
        return self._controllers.get("gcp")
    
    def get_k8s_controller(self) -> K8sController:
        """Get the K8s controller"""
        return self._controllers.get("k8s")
    
    def get_license_controller(self) -> LicenseController:
        """Get the License controller"""
        return self._controllers.get("license")
    
    
    def list_controllers(self) -> Dict[str, str]:
        """List all available controllers"""
        return {name: controller.__class__.__name__ for name, controller in self._controllers.items()}
    
    async def initialize_all(self):
        """Initialize all controllers"""
        for name, controller in self._controllers.items():
            try:
                if hasattr(controller, 'initialize'):
                    await controller.initialize()
                print(f"✅ Initialized {name} controller")
            except Exception as e:
                print(f"❌ Failed to initialize {name} controller: {e}")
    
    async def shutdown_all(self):
        """Shutdown all controllers"""
        for name, controller in self._controllers.items():
            try:
                if hasattr(controller, 'shutdown'):
                    await controller.shutdown()
                print(f"✅ Shutdown {name} controller")
            except Exception as e:
                print(f"❌ Failed to shutdown {name} controller: {e}")
    
    def register_controller(self, name: str, controller: BaseController):
        """Register a custom controller"""
        if self._provider_registry:
            controller.set_provider_registry(self._provider_registry)
        if self._websocket_manager:
            controller.set_websocket_manager(self._websocket_manager)
        
        self._controllers[name] = controller
    
    def unregister_controller(self, name: str):
        """Unregister a controller"""
        if name in self._controllers:
            del self._controllers[name]
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all controllers"""
        for controller in self._controllers.values():
            try:
                await controller.broadcast_message(message)
            except Exception as e:
                print(f"Failed to broadcast to {controller.name}: {e}")
    
    async def get_global_status(self) -> Dict[str, Any]:
        """Get status from all controllers"""
        status = {
            "controllers": {},
            "registry_info": {
                "total_controllers": len(self._controllers),
                "available_controllers": list(self._controllers.keys())
            }
        }
        
        for name, controller in self._controllers.items():
            try:
                controller_status = await controller.get_status()
                status["controllers"][name] = controller_status
            except Exception as e:
                status["controllers"][name] = {"error": str(e)}
        
        return status


# Global registry instance
controller_registry = ControllerRegistry()


def get_controller_registry() -> ControllerRegistry:
    """Get the global controller registry instance"""
    return controller_registry


# Convenience functions
def get_aws_controller() -> AWSController:
    """Get the AWS controller"""
    return controller_registry.get_aws_controller()


def get_gcp_controller() -> GCPController:
    """Get the GCP controller"""
    return controller_registry.get_gcp_controller()


def get_k8s_controller() -> K8sController:
    """Get the K8s controller"""
    return controller_registry.get_k8s_controller()


def get_license_controller() -> LicenseController:
    """Get the License controller"""
    return controller_registry.get_license_controller()




def get_controller(name: str) -> Optional[BaseController]:
    """Get a controller by name"""
    return controller_registry.get_controller(name)