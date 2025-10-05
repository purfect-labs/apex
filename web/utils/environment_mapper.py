"""
Environment Mapper - Abstraction layer for environment handling
Maps standardized UI environments (dev, stage, prod) to actual configuration keys
"""

from typing import Dict, Any, Optional, List
from ..config_loader import get_config


class EnvironmentMapper:
    """Maps standardized UI environments to actual configuration keys"""
    
    # Standard environments used throughout the UI
    STANDARD_ENVIRONMENTS = ["dev", "stage", "prod"]
    
    def __init__(self):
        self.config = get_config()
        self._aws_profile_mapping = self._build_aws_profile_mapping()
        self._gcp_project_mapping = self._build_gcp_project_mapping()
        self._database_config_mapping = self._build_database_config_mapping()
    
    def _build_aws_profile_mapping(self) -> Dict[str, str]:
        """Build mapping from standard environments to AWS profile names"""
        aws_profiles = self.config.get_aws_profiles()
        mapping = {}
        
        # Direct mapping - profiles must be named exactly 'dev', 'stage', 'prod'
        for env in self.STANDARD_ENVIRONMENTS:
            if env in aws_profiles:
                mapping[env] = env
        
        return mapping
    
    def _build_gcp_project_mapping(self) -> Dict[str, str]:
        """Build mapping from standard environments to GCP project names"""
        gcp_config = self.config.get_gcp_config()
        projects = gcp_config.get('projects', {})
        mapping = {}
        
        # Direct mapping - projects must be named exactly 'dev', 'stage', 'prod'
        for env in self.STANDARD_ENVIRONMENTS:
            if env in projects:
                mapping[env] = env
        
        return mapping
    
    def _build_database_config_mapping(self) -> Dict[str, str]:
        """Build mapping from standard environments to database config keys"""
        db_configs = self.config.get_all_database_configs()
        mapping = {}
        
        # Direct mapping - configs must be named exactly 'dev', 'stage', 'prod'
        for env in self.STANDARD_ENVIRONMENTS:
            if env in db_configs:
                mapping[env] = env
        
        return mapping
    
    def get_aws_profile(self, env: str) -> Optional[str]:
        """Get AWS profile name for standard environment"""
        if env not in self.STANDARD_ENVIRONMENTS:
            raise ValueError(f"Environment must be one of: {self.STANDARD_ENVIRONMENTS}")
        
        profile = self._aws_profile_mapping.get(env)
        if not profile:
            raise ValueError(f"No AWS profile mapped for environment: {env}")
        
        return profile
    
    def get_gcp_project(self, env: str) -> Optional[str]:
        """Get GCP project name for standard environment"""
        if env not in self.STANDARD_ENVIRONMENTS:
            raise ValueError(f"Environment must be one of: {self.STANDARD_ENVIRONMENTS}")
        
        project = self._gcp_project_mapping.get(env)
        if not project:
            raise ValueError(f"No GCP project mapped for environment: {env}")
        
        return project
    
    def get_database_config(self, env: str) -> Optional[str]:
        """Get database config key for standard environment"""
        if env not in self.STANDARD_ENVIRONMENTS:
            raise ValueError(f"Environment must be one of: {self.STANDARD_ENVIRONMENTS}")
        
        config_key = self._database_config_mapping.get(env)
        if not config_key:
            raise ValueError(f"No database config mapped for environment: {env}")
        
        return config_key
    
    def get_environment_info(self, env: str) -> Dict[str, Any]:
        """Get comprehensive environment information"""
        if env not in self.STANDARD_ENVIRONMENTS:
            raise ValueError(f"Environment must be one of: {self.STANDARD_ENVIRONMENTS}")
        
        info = {
            "standard_env": env,
            "aws_profile": self._aws_profile_mapping.get(env),
            "gcp_project": self._gcp_project_mapping.get(env),
            "database_config": self._database_config_mapping.get(env),
            "available": True
        }
        
        # Check if environment is fully configured
        info["available"] = bool(info["aws_profile"] or info["gcp_project"])
        
        return info
    
    def get_all_environments(self) -> Dict[str, Dict[str, Any]]:
        """Get information for all standard environments"""
        return {
            env: self.get_environment_info(env)
            for env in self.STANDARD_ENVIRONMENTS
        }
    
    def validate_environment(self, env: str) -> bool:
        """Check if environment is valid"""
        return env in self.STANDARD_ENVIRONMENTS
    
    def get_available_environments(self) -> List[str]:
        """Get list of available standard environments"""
        available = []
        for env in self.STANDARD_ENVIRONMENTS:
            try:
                info = self.get_environment_info(env)
                if info["available"]:
                    available.append(env)
            except ValueError:
                continue
        return available
    
    def refresh_mappings(self):
        """Refresh all mappings from current config"""
        self.config = get_config()
        self._aws_profile_mapping = self._build_aws_profile_mapping()
        self._gcp_project_mapping = self._build_gcp_project_mapping()
        self._database_config_mapping = self._build_database_config_mapping()


# Global instance
_environment_mapper = None


def get_environment_mapper() -> EnvironmentMapper:
    """Get the global environment mapper instance"""
    global _environment_mapper
    if _environment_mapper is None:
        _environment_mapper = EnvironmentMapper()
    return _environment_mapper


# Convenience functions for common operations
def get_aws_profile_for_env(env: str) -> str:
    """Get AWS profile for standard environment"""
    return get_environment_mapper().get_aws_profile(env)


def get_gcp_project_for_env(env: str) -> str:
    """Get GCP project for standard environment"""
    return get_environment_mapper().get_gcp_project(env)


def get_database_config_for_env(env: str) -> str:
    """Get database config for standard environment"""
    return get_environment_mapper().get_database_config(env)


def validate_environment(env: str) -> bool:
    """Validate if environment is a standard environment"""
    return get_environment_mapper().validate_environment(env)


def get_available_environments() -> List[str]:
    """Get list of available environments"""
    return get_environment_mapper().get_available_environments()


def get_environment_constants() -> Dict[str, str]:
    """Get environment constants for use in UI"""
    return {
        "DEV": "dev",
        "STAGE": "stage", 
        "PROD": "prod"
    }