"""
Master Endpoints Summary Route
Provides comprehensive overview of ALL available API endpoints across all providers
"""

from typing import Dict, Any


def setup_endpoints_summary_route(app, controller_registry):
    """Setup master endpoints summary route"""
    
    @app.get("/api/endpoints")
    async def get_all_endpoints():
        """Get comprehensive summary of ALL available API endpoints from all providers"""
        try:
            all_endpoints = {
                "success": True,
                "discovery_timestamp": None,
                "total_endpoints": 0,
                "total_verified_endpoints": 0,
                "providers": {}
            }
            
            # AWS Endpoints
            try:
                aws_controller = controller_registry.get_aws_controller()
                if aws_controller and hasattr(aws_controller, 'get_endpoints'):
                    aws_endpoints = await aws_controller.get_endpoints()
                    if aws_endpoints.get('success'):
                        all_endpoints["providers"]["aws"] = aws_endpoints["endpoints"]
                        all_endpoints["total_endpoints"] += aws_endpoints["endpoints"]["total_endpoints"]
                        all_endpoints["total_verified_endpoints"] += aws_endpoints["endpoints"]["verified_endpoints"]
            except Exception as e:
                all_endpoints["providers"]["aws"] = {"error": str(e)}
            
            # GCP Endpoints  
            try:
                gcp_controller = controller_registry.get_gcp_controller()
                if gcp_controller and hasattr(gcp_controller, 'get_endpoints'):
                    gcp_endpoints = await gcp_controller.get_endpoints()
                    if gcp_endpoints.get('success'):
                        all_endpoints["providers"]["gcp"] = gcp_endpoints["endpoints"]
                        all_endpoints["total_endpoints"] += gcp_endpoints["endpoints"]["total_endpoints"]
                        all_endpoints["total_verified_endpoints"] += gcp_endpoints["endpoints"]["verified_endpoints"]
            except Exception as e:
                all_endpoints["providers"]["gcp"] = {"error": str(e)}
            
            # K8s Endpoints
            try:
                k8s_controller = controller_registry.get_controller("k8s")
                if k8s_controller and hasattr(k8s_controller, 'get_endpoints'):
                    k8s_endpoints = await k8s_controller.get_endpoints()
                    if k8s_endpoints.get('success'):
                        all_endpoints["providers"]["k8s"] = k8s_endpoints["endpoints"]
                        all_endpoints["total_endpoints"] += k8s_endpoints["endpoints"]["total_endpoints"]
                        all_endpoints["total_verified_endpoints"] += k8s_endpoints["endpoints"]["verified_endpoints"]
            except Exception as e:
                all_endpoints["providers"]["k8s"] = {"error": str(e)}
            
            # K8s endpoints are handled by the K8s controller's get_endpoints() method above
            
            # Core API Endpoints (manually defined)
            core_endpoints = {
                "provider": "core",
                "controller": "core_api",
                "available_endpoints": [
                    {
                        "endpoint": "/api/status",
                        "method": "GET",
                        "description": "Get full system status (AWS + GCP + K8s)",
                        "requires_auth": False,
                        "provider_verified": True
                    },
                    {
                        "endpoint": "/api/config", 
                        "method": "GET",
                        "description": "Get configuration information",
                        "requires_auth": False,
                        "provider_verified": True
                    },
                    {
                        "endpoint": "/api/endpoints",
                        "method": "GET", 
                        "description": "THIS ENDPOINT - Comprehensive API discovery",
                        "requires_auth": False,
                        "provider_verified": True
                    },
                    {
                        "endpoint": "/api/auth",
                        "method": "POST",
                        "description": "Authenticate with provider",
                        "requires_auth": False,
                        "parameters": ["provider", "profile?"],
                        "provider_verified": True
                    }
                ],
                "total_endpoints": 4,
                "verified_endpoints": 4
            }
            
            all_endpoints["providers"]["core"] = core_endpoints
            all_endpoints["total_endpoints"] += core_endpoints["total_endpoints"]
            all_endpoints["total_verified_endpoints"] += core_endpoints["verified_endpoints"]
            
            # License endpoints
            license_endpoints = {
                "provider": "license",
                "controller": "license_controller",
                "available_endpoints": [
                    {
                        "endpoint": "/api/license/status",
                        "method": "GET",
                        "description": "Get current license status",
                        "requires_auth": False,
                        "provider_verified": True
                    },
                    {
                        "endpoint": "/api/license/subscription",
                        "method": "GET",
                        "description": "Get subscription and feature information", 
                        "requires_auth": False,
                        "provider_verified": True
                    },
                    {
                        "endpoint": "/api/license/validate",
                        "method": "POST",
                        "description": "Validate license key",
                        "requires_auth": False,
                        "parameters": ["license_key"],
                        "provider_verified": True
                    }
                ],
                "total_endpoints": 3,
                "verified_endpoints": 3
            }
            
            all_endpoints["providers"]["license"] = license_endpoints
            all_endpoints["total_endpoints"] += license_endpoints["total_endpoints"] 
            all_endpoints["total_verified_endpoints"] += license_endpoints["verified_endpoints"]
            
            # Add timestamp
            from datetime import datetime
            all_endpoints["discovery_timestamp"] = datetime.now().isoformat()
            
            return all_endpoints
            
        except Exception as e:
            return {"success": False, "error": str(e)}