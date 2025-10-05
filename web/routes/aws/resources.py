"""
AWS Resource Routes
/api/aws/resources/* endpoints
"""

from fastapi import BackgroundTasks


def setup_aws_resource_routes(app, controller_registry):
    """Setup AWS resource routes"""
    
    @app.get("/api/aws/resources")
    async def aws_resources():
        """Get AWS resources with dynamic account IDs from config"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.get_aws_resources()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/endpoints")
    async def aws_endpoints():
        """Discover available AWS endpoints"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.get_endpoints()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/ec2/instances")
    async def aws_ec2_instances():
        """List EC2 instances"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.list_ec2_instances()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/s3/buckets")
    async def aws_s3_buckets():
        """List S3 buckets"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.list_s3_buckets()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/rds/instances")
    async def aws_rds_instances():
        """List RDS instances"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.list_rds_instances()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/aws/database/status")
    async def aws_database_status():
        """Check AWS database status"""
        try:
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                return await aws_controller.check_database_status()
            else:
                return {"success": False, "error": "AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}