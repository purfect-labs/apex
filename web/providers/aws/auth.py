"""
AWS Authentication Provider
Handles AWS SSO login and authentication status
"""

import json
import os
from typing import Dict, Any, Optional
from ..base_provider import BaseProvider
from web.config_loader import get_config


class AWSAuth(BaseProvider):
    """AWS Authentication Provider"""
    
    def __init__(self):
        super().__init__("aws_auth")
        self.config_loader = get_config()
        self._status_cache = {}
        self._cache_timeout = 300  # 5 minutes
    
    async def authenticate(self, profile: str = "dev", **kwargs) -> Dict[str, Any]:
        """Authenticate with AWS SSO for specified profile"""
        try:
            # Clear cache for fresh authentication attempt
            cache_key = f"profile_status_{profile}"
            if cache_key in self._status_cache:
                del self._status_cache[cache_key]
            
            # Always attempt authentication when manually triggered
            # This ensures SSO links are shown even if already authenticated
            
            # Start authentication process
            import time
            current_timestamp = str(time.time())
            
            await self.broadcast_message({
                'type': 'aws_auth_started',
                'data': {
                    'profile': profile,
                    'message': f'🔐 Starting AWS SSO login for profile: {profile}',
                    'timestamp': current_timestamp
                }
            })
            
            await self.broadcast_message({
                'type': 'aws_auth_output',
                'data': {
                    'output': '🌐 Your browser should open automatically for SSO login...',
                    'profile': profile,
                    'timestamp': current_timestamp
                }
            })
            
            # Execute AWS SSO login with streaming output to show SSO links
            result = await self.execute_command(
                f'aws sso login --profile {profile}',
                env=self.get_env_vars(),
                stream_output=True  # Show SSO links and login progress
            )
            
            if result['success']:
                # Verify authentication worked
                verify_result = await self.get_profile_status(profile)
                if verify_result.get('authenticated', False):
                    await self.broadcast_message({
                        'type': 'aws_auth_success',
                        'data': {
                            'profile': profile,
                            'user': verify_result.get('user'),
                            'account': verify_result.get('account'),
                            'message': f'✅ AWS SSO login successful for {profile}!',
                            'timestamp': verify_result.get('timestamp')
                        }
                    })
                    return verify_result
                else:
                    error_msg = '❌ Login appeared to succeed but identity verification failed'
                    await self.broadcast_message({
                        'type': 'aws_auth_error',
                        'data': {
                            'profile': profile,
                            'error': error_msg,
                            'timestamp': current_timestamp
                        }
                    })
                    return {'success': False, 'error': error_msg}
            else:
                await self.broadcast_message({
                    'type': 'aws_auth_error',
                    'data': {
                        'profile': profile,
                        'error': result.get('stderr', result.get('error', 'Unknown error')),
                        'timestamp': result.get('timestamp')
                    }
                })
                return result
                
        except Exception as e:
            error_msg = f'Failed to authenticate AWS profile {profile}: {str(e)}'
            await self.broadcast_message({
                'type': 'aws_auth_error',
                'data': {
                    'profile': profile,
                    'error': error_msg,
                    'timestamp': current_timestamp
                }
            })
            return {'success': False, 'error': error_msg}
    
    async def authenticate_all_profiles(self) -> Dict[str, Any]:
        """Authenticate all configured AWS profiles"""
        profiles = self.config_loader.get_aws_profiles()
        results = {}
        
        await self.broadcast_message({
            'type': 'aws_auth_started',
            'data': {
                'message': '🚀 Starting AWS SSO authentication for all profiles...',
                'profiles': list(profiles.keys()),
                'timestamp': None
            }
        })
        
        for profile_name in profiles.keys():
            result = await self.authenticate(profile=profile_name)
            results[profile_name] = result
        
        all_success = all(r.get('success', False) for r in results.values())
        
        await self.broadcast_message({
            'type': 'aws_auth_all_completed',
            'data': {
                'success': all_success,
                'results': results,
                'message': '✅ All AWS profiles authenticated!' if all_success else '⚠️ Some profiles failed to authenticate',
                'timestamp': None
            }
        })
        
        return {
            'success': all_success,
            'profiles': results
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get authentication status for all AWS profiles"""
        profiles = self.config_loader.get_aws_profiles()
        status = {}
        
        for profile_name in profiles.keys():
            profile_status = await self.get_profile_status(profile_name)
            status[profile_name] = profile_status
        
        return {
            'profiles': status,
            'all_authenticated': all(p.get('authenticated', False) for p in status.values()),
            'configured_profiles': list(profiles.keys())
        }
    
    async def get_profile_status(self, profile: str) -> Dict[str, Any]:
        """Get authentication status for specific profile with 5-minute caching"""
        import time
        
        # Check cache first
        cache_key = f"profile_status_{profile}"
        if cache_key in self._status_cache:
            cached_result, cached_time = self._status_cache[cache_key]
            if time.time() - cached_time < self._cache_timeout:
                return cached_result
        
        try:
            result = await self.execute_command(
                f'aws sts get-caller-identity --profile {profile}',
                env=self.get_env_vars(),
                stream_output=True  # Show status checks for debugging
            )
            
            if result['success']:
                identity = json.loads(result['stdout'])
                status_result = {
                    'authenticated': True,
                    'user': identity.get('Arn', '').split('/')[-1],
                    'account': identity.get('Account'),
                    'arn': identity.get('Arn'),
                    'profile': profile,
                    'timestamp': result['timestamp']
                }
            else:
                status_result = {
                    'authenticated': False,
                    'profile': profile,
                    'error': result.get('stderr', 'Unknown error'),
                    'timestamp': result['timestamp']
                }
            
            # Cache the result for 5 minutes
            import time
            self._status_cache[cache_key] = (status_result, time.time())
            return status_result
                
        except Exception as e:
            return {
                'authenticated': False,
                'profile': profile,
                'error': str(e),
                'timestamp': None
            }
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get AWS-specific environment variables"""
        env_vars = {
            'HOME': os.path.expanduser('~'),
            'AWS_CONFIG_FILE': os.path.expanduser('~/.aws/config'),
            'AWS_SHARED_CREDENTIALS_FILE': os.path.expanduser('~/.aws/credentials'),
            'AWS_DEFAULT_REGION': 'us-east-1',
            'AWS_REGION': 'us-east-1'
        }
        
        return env_vars