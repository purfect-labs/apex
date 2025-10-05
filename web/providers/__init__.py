"""
APEX API Caller Package - Provider modules for different cloud services
"""

from .base_provider import BaseProvider
from .aws.auth import AWSAuth
from .gcp.auth import GCPAuth
from .gcp.k8s import GCPK8s
from .license import LicenseProvider

from typing import Dict, Any, Optional


class ProviderRegistry:
    """Registry for managing all providers"""
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._websocket_manager = None
    
    def register_provider(self, name: str, provider: BaseProvider):
        """Register a provider"""
        if self._websocket_manager:
            provider.broadcast_message = self._websocket_manager.broadcast_message
        self._providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get a provider by name"""
        return self._providers.get(name)
    
    def set_websocket_manager(self, websocket_manager):
        """Set WebSocket manager for all providers"""
        self._websocket_manager = websocket_manager
        for provider in self._providers.values():
            provider.broadcast_message = websocket_manager.broadcast_message
    
    def list_providers(self) -> Dict[str, str]:
        """List all registered providers"""
        return {name: provider.__class__.__name__ for name, provider in self._providers.items()}


# Global registry instance
_provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry instance"""
    return _provider_registry


__all__ = [
    'BaseProvider',
    'AWSAuth',
    'GCPAuth', 
    'GCPK8s',
    'LicenseProvider',
    'ProviderRegistry',
    'get_provider_registry'
]
