"""
Core Routes Module
System-wide routes like status, config, auth
"""

from .config import setup_core_config_routes

def setup_core_routes(app, controller_registry):
    """Setup core system routes"""
    setup_core_config_routes(app, controller_registry)
