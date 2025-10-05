"""
Base Controller for APEX Web Controllers
Handles common functionality and provider coordination
"""

from abc import ABC
from typing import Dict, Any, Optional
from datetime import datetime


class BaseController(ABC):
    """Base class for all APEX controllers"""
    
    def __init__(self, name: str):
        self.name = name
        self.providers = {}
        self.broadcast_callback = None
    
    def set_providers(self, **providers):
        """Set provider instances for this controller"""
        self.providers.update(providers)
    
    def set_broadcast_callback(self, callback):
        """Set callback function for broadcasting messages"""
        self.broadcast_callback = callback
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if self.broadcast_callback:
            await self.broadcast_callback(message)
    
    async def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log an action with optional details"""
        message = {
            'type': 'action_log',
            'data': {
                'controller': self.name,
                'action': action,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            }
        }
        await self.broadcast_message(message)
    
    async def handle_error(self, error: str, context: str = ""):
        """Handle and broadcast errors"""
        message = {
            'type': 'error',
            'data': {
                'controller': self.name,
                'error': error,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
        }
        await self.broadcast_message(message)
    
    def set_provider_registry(self, provider_registry):
        """Set provider registry for accessing providers"""
        self.provider_registry = provider_registry
    
    def set_websocket_manager(self, websocket_manager):
        """Set WebSocket manager for broadcasting"""
        self.websocket_manager = websocket_manager
        self.set_broadcast_callback(websocket_manager.broadcast_message)
    
    def get_provider(self, provider_name: str):
        """Get a provider from the registry or local providers"""
        if hasattr(self, 'provider_registry') and self.provider_registry:
            return self.provider_registry.get_provider(provider_name)
        return self.providers.get(provider_name)
