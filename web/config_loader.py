"""
APEX Configuration Loader - New Structure
Loads all configuration files into memory for easy access using environment variables
"""

import os
import yaml
import configparser
import glob
from pathlib import Path
from typing import Dict, Any, Optional


class APEXConfigLoader:
    """Load and manage all APEX configuration files with new structure"""
    
    def __init__(self, config_dir: Optional[str] = None):
        # Use environment variables if available, otherwise fallback
        if config_dir:
            self.config_dir = Path(config_dir)
        elif 'APEX_CONFIG_DIR' in os.environ:
            self.config_dir = Path(os.environ['APEX_CONFIG_DIR'])
        else:
            self.config_dir = Path(__file__).parent.parent / "config"
        
        self.static_config_dir = self.config_dir / "static"
        self.templates_dir = self.config_dir / "templates"
        
        # Global memory space for configs organized by filename prefix
        self.static_configs = {}  # e.g., {'gcp': {...}, 'gh': {...}, 'circle': {...}}
        self.rendered_configs = {}  # e.g., {'aws.db': {...}, 'aws.sso': {...}}
        
        # Unified config for backward compatibility
        self.config = {}
        
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files from both static and rendered configs"""
        try:
            # Load static configs (by filename prefix)
            self._load_static_configs()
            
            # Load rendered configs (from main config dir)
            self._load_rendered_configs()
            
            # Create unified config for backward compatibility
            self._create_unified_config()
            
        except Exception as e:
            self._set_defaults()
    
    def _load_static_configs(self):
        """Load all static configuration files by filename prefix"""
        if not self.static_config_dir.exists():
            return
        
        # Find all .config files in static directory
        config_files = glob.glob(str(self.static_config_dir / "*.config"))
        
        for config_file in config_files:
            file_path = Path(config_file)
            # Get filename prefix (e.g., 'gcp' from 'gcp.config')
            prefix = file_path.stem.split('.')[0]
            
            try:
                config_data = self._load_config_file(file_path)
                if config_data:
                    self.static_configs[prefix] = config_data
            except Exception as e:
                # Silently fail
                pass
    
    def _load_rendered_configs(self):
        """Load rendered configuration files from main config directory"""
        # Find all .config files in main config directory (not subdirs)
        config_files = glob.glob(str(self.config_dir / "*.config"))
        
        for config_file in config_files:
            file_path = Path(config_file)
            # Get first two parts of filename (e.g., 'aws.db' from 'aws.db.config')
            filename_parts = file_path.stem.split('.')
            if len(filename_parts) >= 2:
                prefix = f"{filename_parts[0]}.{filename_parts[1]}"
            else:
                prefix = filename_parts[0]
            
            try:
                config_data = self._load_config_file(file_path)
                if config_data:
                    self.rendered_configs[prefix] = config_data
            except Exception as e:
                pass
    
    def _load_config_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load a single configuration file, auto-detecting format"""
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                
            if not content:
                return None
            
            # Try YAML first
            try:
                config_data = yaml.safe_load(content)
                if config_data:
                    return config_data
            except yaml.YAMLError:
                pass
            
            # Try INI format
            try:
                config_parser = configparser.ConfigParser()
                config_parser.read_string(content)
                
                config_data = {}
                for section_name in config_parser.sections():
                    section = dict(config_parser[section_name])
                    
                    if section_name.startswith('profile '):
                        # AWS profile section
                        profile_name = section_name.replace('profile ', '')
                        if 'profiles' not in config_data:
                            config_data['profiles'] = {}
                        config_data['profiles'][profile_name] = section
                        
                    elif section_name.startswith('sso-session '):
                        # AWS SSO session section
                        session_name = section_name.replace('sso-session ', '')
                        if 'sso_sessions' not in config_data:
                            config_data['sso_sessions'] = {}
                        config_data['sso_sessions'][session_name] = section
                    else:
                        # Regular section
                        config_data[section_name] = section
                
                return config_data
                
            except configparser.Error:
                pass
            
            # If neither format works, return None
            return None
            
        except Exception as e:
            return None
    
    def _create_unified_config(self):
        """Create unified config for backward compatibility"""
        self.config = {}
        
        # Map static configs
        if 'gcp' in self.static_configs:
            gcp_data = self.static_configs['gcp']
            # Extract 'gcp' key if it exists, otherwise use the whole config
            if 'gcp' in gcp_data:
                self.config['gcp'] = gcp_data['gcp']
            else:
                self.config['gcp'] = gcp_data
        
        # Map rendered configs
        if 'aws.sso' in self.rendered_configs:
            self.config['aws'] = self.rendered_configs['aws.sso']
        
        if 'aws.db' in self.rendered_configs:
            self.config['databases'] = self.rendered_configs['aws.db']
        
        # Add other static configs
        for prefix, config_data in self.static_configs.items():
            if prefix not in ['gcp']:  # Already handled above
                self.config[prefix] = config_data
    
    def _set_defaults(self):
        """Set default configuration values"""
        if not hasattr(self, 'config') or not self.config:
            self.config = {}
        
        if 'aws' not in self.config:
            self.config['aws'] = {}
        
        if 'gcp' not in self.config:
            self.config['gcp'] = {}
        
        if 'databases' not in self.config:
            self.config['databases'] = {}
        
        # Set default AWS region
        if 'region' not in self.config['aws']:
            self.config['aws']['region'] = 'us-east1'
    
    # Backward compatibility methods
    def get_aws_profiles(self) -> Dict[str, Any]:
        """Get AWS profiles configuration"""
        return self.config.get('aws', {}).get('profiles', {})
    
    def get_aws_sso_sessions(self) -> Dict[str, Any]:
        """Get AWS SSO sessions configuration"""
        return self.config.get('aws', {}).get('sso_sessions', {})
    
    def get_database_config(self, cloud: str, env: str) -> Optional[Dict[str, Any]]:
        """Get database configuration for specific cloud/environment"""
        databases = self.config.get('databases', {})
        return databases.get(cloud, {}).get(env)
    
    def get_all_database_configs(self) -> Dict[str, Any]:
        """Get all database configurations"""
        return self.config.get('databases', {})
    
    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS configuration"""
        return self.config.get('aws', {})
    
    def get_gcp_config(self) -> Dict[str, Any]:
        """Get GCP configuration"""
        return self.config.get('gcp', {})
    
    # New methods for direct access to organized configs
    def get_static_config(self, prefix: str) -> Optional[Dict[str, Any]]:
        """Get static config by prefix (e.g., 'gcp', 'gh', 'circle')"""
        return self.static_configs.get(prefix)
    
    def get_rendered_config(self, prefix: str) -> Optional[Dict[str, Any]]:
        """Get rendered config by prefix (e.g., 'aws.db', 'aws.sso')"""
        return self.rendered_configs.get(prefix)
    
    def get_all_static_configs(self) -> Dict[str, Any]:
        """Get all static configurations"""
        return self.static_configs
    
    def get_all_rendered_configs(self) -> Dict[str, Any]:
        """Get all rendered configurations"""
        return self.rendered_configs
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get the full unified configuration"""
        return self.config
    
    def reload(self):
        """Reload all configuration files"""
        self.static_configs = {}
        self.rendered_configs = {}
        self.config = {}
        self._load_all_configs()


# Global config instance
_config_loader = None

def get_config() -> APEXConfigLoader:
    """Get global configuration instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = APEXConfigLoader()
    return _config_loader