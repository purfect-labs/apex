"""
Core Configuration Routes
/api/config/* endpoints
"""

def setup_core_config_routes(app, controller_registry):
    """Setup core configuration routes"""
    
    @app.get("/api/config/profiles")
    async def get_available_profiles():
        """Get available profiles from config"""
        try:
            from web.config_loader import get_config
            config = get_config()
            
            # Get AWS profiles
            aws_profiles = config.get_aws_profiles()
            
            # Get GCP projects (if configured)
            gcp_config = config.get_gcp_config()
            gcp_projects = gcp_config.get('projects', {}) if gcp_config else {}
            
            return {
                "success": True,
                "aws_profiles": list(aws_profiles.keys()),
                "aws_profile_details": aws_profiles,
                "gcp_projects": list(gcp_projects.keys()),
                "gcp_project_details": gcp_projects
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/config")
    async def get_config_info():
        """Get configuration info"""
        try:
            from web.config_loader import get_config
            config = get_config()
            
            return {
                "success": True,
                "aws": {
                    "profiles": list(config.get_aws_profiles().keys()),
                    "configured": bool(config.get_aws_profiles())
                },
                "gcp": {
                    "projects": list(config.get_gcp_config().get('projects', {}).keys()) if config.get_gcp_config() else [],
                    "configured": bool(config.get_gcp_config())
                },
                "database": {
                    "configured": bool(config.get_database_config())
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}