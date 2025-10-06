"""
K8s Routes Module
Comprehensive Kubernetes resource management and context switching
"""

from .resources import setup_k8s_resource_routes


def setup_k8s_routes(app, controller_registry):
    """Setup comprehensive K8s routes"""
    # Resource management routes
    setup_k8s_resource_routes(app, controller_registry)
