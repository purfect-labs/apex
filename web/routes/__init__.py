"""
Routes Module
Organizes all API routes by provider and capability
"""

from .aws import setup_aws_routes
from .gcp import setup_gcp_routes  
from .k8s import setup_k8s_routes
from .core import setup_core_routes


def setup_all_routes(app, controller_registry):
    """Setup all routes organized by provider"""
    
    # Core system routes (status, config, etc)
    setup_core_routes(app, controller_registry)
    
    # Provider-specific routes
    setup_aws_routes(app, controller_registry)
    setup_gcp_routes(app, controller_registry)
    setup_k8s_routes(app, controller_registry)
    
    print("📡 All routes organized by provider and capability")
    print("   - AWS: /api/aws/*")
    print("   - GCP: /api/gcp/*") 
    print("   - K8s: /api/k8s/*")
    print("   - Core: /api/{status,config,auth}")


def list_all_routes(app):
    """List all registered routes for debugging"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': getattr(route, 'name', 'unnamed')
            })
    return routes