"""
Core Routes Module
System-wide routes like status, config, auth
"""

from .config import setup_core_config_routes
from .endpoints import setup_endpoints_summary_route

def setup_core_routes(app, controller_registry):
    """Setup core system routes"""
    setup_core_config_routes(app, controller_registry)
    setup_endpoints_summary_route(app, controller_registry)
