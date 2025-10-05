#!/usr/bin/env python3
"""
License Controller - Business Logic Layer
Handles license validation, activation, and subscription management
Following APEX three-tier architecture pattern
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .base_controller import BaseController


class LicenseController(BaseController):
    """License management business logic controller"""
    
    def __init__(self):
        super().__init__("license")
        self._current_license = None
        self._license_cache_expiry = None

    async def get_license_status(self) -> Dict[str, Any]:
        """Get current license status with caching"""
        try:
            await self.log_action("get_license_status", {"source": "controller"})
            
            # Check cache first
            if self._current_license and self._license_cache_expiry:
                if datetime.now() < self._license_cache_expiry:
                    await self.log_action("license_status_cached", {"status": "cached"})
                    return self._current_license

            # Get fresh license status from provider
            license_provider = self.get_provider("license")
            if not license_provider:
                error_msg = "License provider not available"
                await self.handle_error(error_msg, "get_license_status")
                return {"success": False, "error": error_msg}

            status = await license_provider.get_license_status()
            
            # Cache the result for 5 minutes
            self._current_license = status
            self._license_cache_expiry = datetime.now() + timedelta(minutes=5)
            
            # Broadcast license status update
            await self.broadcast_message({
                'type': 'license_status_updated',
                'data': {
                    'status': status.get('status', 'unknown'),
                    'expires': status.get('expires'),
                    'user_email': status.get('user_email'),
                    'features': status.get('features', []),
                    'days_remaining': status.get('days_remaining')
                }
            })
            
            await self.log_action("license_status_retrieved", {
                "status": status.get('status', 'unknown'),
                "expires": status.get('expires'),
                "features": len(status.get('features', []))
            })
            
            return status
            
        except Exception as e:
            error_msg = f"Failed to get license status: {str(e)}"
            await self.handle_error(error_msg, "get_license_status")
            return {"success": False, "error": error_msg}

    async def activate_license(self, license_key: str, user_email: str = None) -> Dict[str, Any]:
        """Activate a license key with validation and storage"""
        try:
            await self.log_action("activate_license_start", {
                "user_email": user_email,
                "key_prefix": license_key[:8] + "..." if len(license_key) > 8 else "short_key"
            })
            
            # Broadcast activation start
            await self.broadcast_message({
                'type': 'license_activation_started',
                'data': {
                    'message': '🔑 Validating license key...',
                    'user_email': user_email
                }
            })

            # Get license provider
            license_provider = self.get_provider("license")
            if not license_provider:
                error_msg = "License provider not available"
                await self.handle_error(error_msg, "activate_license")
                return {"success": False, "error": error_msg}

            # Validate and activate license
            result = await license_provider.activate_license(license_key, user_email)
            
            if result.get("success", False):
                # Clear cache to force refresh
                self._current_license = None
                self._license_cache_expiry = None
                
                # Broadcast success
                await self.broadcast_message({
                    'type': 'license_activation_success',
                    'data': {
                        'message': '✅ License activated successfully!',
                        'user_email': result.get('user_email'),
                        'expires': result.get('expires'),
                        'features': result.get('features', []),
                        'license_type': result.get('license_type', 'standard')
                    }
                })
                
                await self.log_action("license_activation_success", {
                    "user_email": result.get('user_email'),
                    "license_type": result.get('license_type'),
                    "expires": result.get('expires'),
                    "features": result.get('features', [])
                })
                
                # Get fresh status after activation
                status = await self.get_license_status()
                return status
            else:
                # Broadcast failure
                error_msg = result.get('error', 'License activation failed')
                await self.broadcast_message({
                    'type': 'license_activation_failed',
                    'data': {
                        'message': f'❌ License activation failed: {error_msg}',
                        'error': error_msg
                    }
                })
                
                await self.log_action("license_activation_failed", {"error": error_msg})
                return result
                
        except Exception as e:
            error_msg = f"License activation failed: {str(e)}"
            await self.handle_error(error_msg, "activate_license")
            
            await self.broadcast_message({
                'type': 'license_activation_failed',
                'data': {
                    'message': f'❌ License activation failed: {error_msg}',
                    'error': error_msg
                }
            })
            
            return {"success": False, "error": error_msg}

    async def generate_trial_license(self, user_email: str, days: int = 7) -> Dict[str, Any]:
        """Generate a trial license for testing/demo purposes"""
        try:
            await self.log_action("generate_trial_start", {
                "user_email": user_email,
                "days": days
            })
            
            # Broadcast trial generation start
            await self.broadcast_message({
                'type': 'trial_generation_started',
                'data': {
                    'message': f'🆓 Generating {days}-day trial license...',
                    'user_email': user_email,
                    'days': days
                }
            })

            # Get license provider
            license_provider = self.get_provider("license")
            if not license_provider:
                error_msg = "License provider not available"
                await self.handle_error(error_msg, "generate_trial_license")
                return {"success": False, "error": error_msg}

            # Generate trial license
            result = await license_provider.generate_trial_license(user_email, days)
            
            if result.get("success", False):
                await self.broadcast_message({
                    'type': 'trial_generation_success',
                    'data': {
                        'message': f'✅ {days}-day trial license generated!',
                        'license_key': result.get('license_key'),
                        'user_email': user_email,
                        'expires': result.get('expires'),
                        'days': days
                    }
                })
                
                await self.log_action("trial_generation_success", {
                    "user_email": user_email,
                    "days": days,
                    "expires": result.get('expires')
                })
                
                return result
            else:
                error_msg = result.get('error', 'Trial generation failed')
                await self.broadcast_message({
                    'type': 'trial_generation_failed',
                    'data': {
                        'message': f'❌ Trial generation failed: {error_msg}',
                        'error': error_msg
                    }
                })
                
                await self.log_action("trial_generation_failed", {"error": error_msg})
                return result
                
        except Exception as e:
            error_msg = f"Trial generation failed: {str(e)}"
            await self.handle_error(error_msg, "generate_trial_license")
            
            await self.broadcast_message({
                'type': 'trial_generation_failed',
                'data': {
                    'message': f'❌ Trial generation failed: {error_msg}',
                    'error': error_msg
                }
            })
            
            return {"success": False, "error": error_msg}

    async def deactivate_license(self) -> Dict[str, Any]:
        """Deactivate current license (logout)"""
        try:
            await self.log_action("deactivate_license_start", {})
            
            # Broadcast deactivation start
            await self.broadcast_message({
                'type': 'license_deactivation_started',
                'data': {
                    'message': '🔓 Deactivating license...'
                }
            })

            # Get license provider
            license_provider = self.get_provider("license")
            if not license_provider:
                error_msg = "License provider not available"
                await self.handle_error(error_msg, "deactivate_license")
                return {"success": False, "error": error_msg}

            # Deactivate license
            result = await license_provider.deactivate_license()
            
            if result.get("success", False):
                # Clear cache
                self._current_license = None
                self._license_cache_expiry = None
                
                await self.broadcast_message({
                    'type': 'license_deactivation_success',
                    'data': {
                        'message': '✅ License deactivated successfully',
                        'status': 'inactive'
                    }
                })
                
                await self.log_action("license_deactivation_success", {})
                return result
            else:
                error_msg = result.get('error', 'License deactivation failed')
                await self.broadcast_message({
                    'type': 'license_deactivation_failed',
                    'data': {
                        'message': f'❌ Deactivation failed: {error_msg}',
                        'error': error_msg
                    }
                })
                
                await self.log_action("license_deactivation_failed", {"error": error_msg})
                return result
                
        except Exception as e:
            error_msg = f"License deactivation failed: {str(e)}"
            await self.handle_error(error_msg, "deactivate_license")
            
            await self.broadcast_message({
                'type': 'license_deactivation_failed',
                'data': {
                    'message': f'❌ Deactivation failed: {error_msg}',
                    'error': error_msg
                }
            })
            
            return {"success": False, "error": error_msg}

    async def get_subscription_info(self) -> Dict[str, Any]:
        """Get subscription and feature information"""
        try:
            # Get current license status first
            license_status = await self.get_license_status()
            
            if not license_status.get("success", True):
                return license_status
            
            # Extract subscription information
            subscription_info = {
                "success": True,
                "user_email": license_status.get("user_email"),
                "license_type": license_status.get("license_type", "standard"),
                "status": license_status.get("status", "inactive"),
                "expires": license_status.get("expires"),
                "days_remaining": license_status.get("days_remaining"),
                "features": license_status.get("features", []),
                "feature_details": {
                    "basic": {
                        "name": "Basic Features", 
                        "enabled": "basic" in license_status.get("features", []),
                        "description": "Core cloud operations and terminal access"
                    },
                    "advanced": {
                        "name": "Advanced Operations",
                        "enabled": "advanced" in license_status.get("features", []),
                        "description": "Multi-cloud management and automation"
                    },
                    "premium": {
                        "name": "Premium Features",
                        "enabled": "premium" in license_status.get("features", []),
                        "description": "Enterprise features and priority support"
                    }
                },
                "is_trial": license_status.get("license_type") == "trial",
                "can_generate_trial": license_status.get("status") == "inactive"
            }
            
            await self.log_action("subscription_info_retrieved", {
                "status": subscription_info["status"],
                "features": len(subscription_info["features"]),
                "is_trial": subscription_info["is_trial"]
            })
            
            return subscription_info
            
        except Exception as e:
            error_msg = f"Failed to get subscription info: {str(e)}"
            await self.handle_error(error_msg, "get_subscription_info")
            return {"success": False, "error": error_msg}

    async def validate_license_key(self, license_key: str) -> Dict[str, Any]:
        """Validate a license key without activating it"""
        try:
            await self.log_action("validate_license_key_start", {
                "key_prefix": license_key[:8] + "..." if len(license_key) > 8 else "short_key"
            })
            
            # Get license provider
            license_provider = self.get_provider("license")
            if not license_provider:
                error_msg = "License provider not available"
                await self.handle_error(error_msg, "validate_license_key")
                return {"valid": False, "error": error_msg}

            # Validate license key format and authenticity
            result = await license_provider.validate_license_key(license_key)
            
            await self.log_action("license_key_validated", {
                "valid": result.get('valid', False),
                "key_prefix": license_key[:8] + "..." if len(license_key) > 8 else "short_key"
            })
            
            return result
                
        except Exception as e:
            error_msg = f"License key validation failed: {str(e)}"
            await self.handle_error(error_msg, "validate_license_key")
            return {"valid": False, "error": error_msg}

    async def validate_feature_access(self, feature: str) -> bool:
        """Check if current license allows access to specific feature"""
        try:
            license_status = await self.get_license_status()
            
            if not license_status.get("success", True):
                return False
            
            if license_status.get("status") != "active":
                return False
            
            features = license_status.get("features", [])
            return feature in features
            
        except Exception as e:
            await self.log_action("feature_validation_error", {
                "feature": feature,
                "error": str(e)
            })
            return False
