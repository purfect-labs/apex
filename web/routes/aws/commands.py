"""
AWS Command Execution Routes
/api/aws/execute/* endpoints
"""

from fastapi import BackgroundTasks


def setup_aws_command_routes(app, controller_registry):
    """Setup AWS command execution routes"""
    
    @app.post("/api/aws/execute")
    async def aws_execute_command(request: dict, background_tasks: BackgroundTasks):
        """Execute AWS command"""
        try:
            command = request.get('command', '')
            environment = request.get('environment', 'dev')
            
            if not command:
                return {"success": False, "error": "No command provided"}
            
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                background_tasks.add_task(
                    aws_controller.execute_aws_command,
                    command=command,
                    environment=environment
                )
                return {
                    "success": True,
                    "message": f"AWS command execution started: {command}",
                    "command": command,
                    "environment": environment
                }
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/aws/switch-profile")
    async def aws_switch_profile(request: dict, background_tasks: BackgroundTasks):
        """Switch AWS profile"""
        try:
            profile = request.get('profile', 'dev')
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                background_tasks.add_task(
                    aws_controller.switch_aws_profile,
                    profile=profile
                )
                return {
                    "success": True,
                    "message": f"AWS profile switching to {profile}",
                    "profile": profile
                }
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}