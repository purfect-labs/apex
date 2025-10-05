"""
AWS Routes Module
Handles all AWS-related API routes
"""

from .auth import setup_aws_auth_routes
from .resources import setup_aws_resource_routes
from .commands import setup_aws_command_routes

def setup_aws_routes(app, controller_registry):
    """Setup all AWS routes"""
    setup_aws_auth_routes(app, controller_registry)
    setup_aws_resource_routes(app, controller_registry) 
    setup_aws_command_routes(app, controller_registry)