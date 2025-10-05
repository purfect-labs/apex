"""
AWS Authentication Routes
/api/aws/auth/* endpoints
"""

from fastapi import BackgroundTasks


def setup_aws_auth_routes(app, controller_registry):
    """Setup AWS authentication routes"""
    
    @app.post("/api/aws/auth")
    async def aws_authenticate(request: dict, background_tasks: BackgroundTasks):
        """Authenticate with AWS SSO for specified profile"""
        try:
            profile = request.get('profile', 'dev')
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                background_tasks.add_task(
                    aws_controller.authenticate,
                    profile=profile
                )
                return {
                    "success": True,
                    "message": f"AWS SSO authentication started for {profile}",
                    "profile": profile
                }
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/aws/auth/all")
    async def aws_authenticate_all(background_tasks: BackgroundTasks):
        """Authenticate all AWS profiles"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                background_tasks.add_task(aws_controller.authenticate_all_profiles)
                return {
                    "success": True,
                    "message": "AWS SSO authentication started for all profiles"
                }
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/status")
    async def aws_status():
        """Get AWS authentication status for all profiles"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.get_status()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/profiles")
    async def aws_profiles():
        """Get available AWS profiles"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.list_aws_profiles()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/identity")
    async def aws_identity():
        """Get current AWS identity (sts get-caller-identity)"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.get_current_identity()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/regions")
    async def aws_regions():
        """Get available AWS regions"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.list_aws_regions()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}