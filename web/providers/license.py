#!/usr/bin/env python3
"""
License Provider - Integration Layer
Handles direct license operations, keychain access, and license generation
Following APEX BaseProvider pattern
"""

import json
import base64
import keyring
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from .base_provider import BaseProvider


class LicenseProvider(BaseProvider):
    """License operations provider with keychain integration"""
    
    def __init__(self):
        super().__init__("license")
        # Fixed demo encryption key - for production use proper key management
        self._demo_key = base64.urlsafe_b64encode(b"apex_demo_license_key_32_chars_!").decode()
        self._fernet = Fernet(self._demo_key.encode())
        self._keychain_service = "apex-license"
        self._keychain_account = "APEX"

    async def get_license_status(self) -> Dict[str, Any]:
        """Get current license status from keychain"""
        try:
            # Get stored license from keychain
            stored_license = keyring.get_password(self._keychain_service, self._keychain_account)
            
            if not stored_license:
                return {
                    "success": True,
                    "status": "inactive",
                    "message": "No license found",
                    "user_email": None,
                    "expires": None,
                    "features": [],
                    "license_type": None,
                    "days_remaining": None
                }
            
            # Validate and decode license
            license_data = await self._validate_license_key(stored_license)
            
            if not license_data.get("valid", False):
                # License is invalid, clear it
                await self.deactivate_license()
                return {
                    "success": True,
                    "status": "invalid",
                    "message": license_data.get("error", "License validation failed"),
                    "user_email": None,
                    "expires": None,
                    "features": [],
                    "license_type": None,
                    "days_remaining": None
                }
            
            # Return active license status
            license_info = license_data["license_info"]
            expires_str = license_info.get("expires")
            days_remaining = None
            
            if expires_str:
                try:
                    expires_date = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                    days_remaining = max(0, (expires_date - datetime.now()).days)
                except:
                    pass
            
            return {
                "success": True,
                "status": "active",
                "message": "License is active",
                "user_email": license_info.get("user_email"),
                "user_name": license_info.get("user_name"),
                "expires": expires_str,
                "features": license_info.get("features", []),
                "license_type": license_info.get("license_type", "standard"),
                "days_remaining": days_remaining
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get license status: {str(e)}",
                "status": "error"
            }

    async def activate_license(self, license_key: str, user_email: str = None) -> Dict[str, Any]:
        """Activate a license key with validation and keychain storage"""
        try:
            # Validate the license key
            validation_result = await self._validate_license_key(license_key)
            
            if not validation_result.get("valid", False):
                return {
                    "success": False,
                    "error": validation_result.get("error", "Invalid license key")
                }
            
            license_info = validation_result["license_info"]
            
            # Additional email validation if provided
            if user_email and license_info.get("user_email") != user_email:
                return {
                    "success": False,
                    "error": f"License key does not match email {user_email}"
                }
            
            # Store license in keychain
            keyring.set_password(self._keychain_service, self._keychain_account, license_key)
            
            # Return activation result
            return {
                "success": True,
                "message": "License activated successfully",
                "user_email": license_info.get("user_email"),
                "user_name": license_info.get("user_name"),
                "expires": license_info.get("expires"),
                "features": license_info.get("features", []),
                "license_type": license_info.get("license_type", "standard")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"License activation failed: {str(e)}"
            }

    async def deactivate_license(self) -> Dict[str, Any]:
        """Remove license from keychain"""
        try:
            keyring.delete_password(self._keychain_service, self._keychain_account)
            return {
                "success": True,
                "message": "License deactivated successfully"
            }
        except keyring.errors.PasswordDeleteError:
            return {
                "success": True,
                "message": "No license was active"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"License deactivation failed: {str(e)}"
            }

    async def generate_trial_license(self, user_email: str, days: int = 7) -> Dict[str, Any]:
        """Generate a trial license for the given email"""
        try:
            # Create trial license data
            expires_date = datetime.now() + timedelta(days=days)
            
            license_data = {
                "user_email": user_email,
                "user_name": user_email.split('@')[0].title(),  # Simple name from email
                "expires": expires_date.isoformat(),
                "features": ["basic"],  # Trial gets basic features
                "license_type": "trial",
                "generated_at": datetime.now().isoformat()
            }
            
            # Encrypt and encode the license
            license_json = json.dumps(license_data)
            encrypted_data = self._fernet.encrypt(license_json.encode())
            license_key = base64.urlsafe_b64encode(encrypted_data).decode()
            
            # Format as readable license key (XXXX-XXXX-XXXX-XXXX)
            formatted_key = self._format_license_key(license_key)
            
            return {
                "success": True,
                "license_key": formatted_key,
                "user_email": user_email,
                "expires": expires_date.isoformat(),
                "days": days,
                "message": f"{days}-day trial license generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Trial license generation failed: {str(e)}"
            }

    async def generate_full_license(self, user_email: str, user_name: str, 
                                   days: int, features: list) -> Dict[str, Any]:
        """Generate a full license with specified features"""
        try:
            # Create full license data
            expires_date = datetime.now() + timedelta(days=days)
            
            license_data = {
                "user_email": user_email,
                "user_name": user_name,
                "expires": expires_date.isoformat(),
                "features": features,
                "license_type": "standard",
                "generated_at": datetime.now().isoformat()
            }
            
            # Encrypt and encode the license
            license_json = json.dumps(license_data)
            encrypted_data = self._fernet.encrypt(license_json.encode())
            license_key = base64.urlsafe_b64encode(encrypted_data).decode()
            
            # Format as readable license key
            formatted_key = self._format_license_key(license_key)
            
            return {
                "success": True,
                "license_key": formatted_key,
                "user_email": user_email,
                "user_name": user_name,
                "expires": expires_date.isoformat(),
                "features": features,
                "days": days,
                "message": f"{days}-day license generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"License generation failed: {str(e)}"
            }

    async def _validate_license_key(self, license_key: str) -> Dict[str, Any]:
        """Validate and decode a license key"""
        try:
            # Remove formatting if present (XXXX-XXXX-XXXX-XXXX → continuous string)
            clean_key = license_key.replace("-", "").replace(" ", "")
            
            # Decode and decrypt the license
            try:
                encrypted_data = base64.urlsafe_b64decode(clean_key.encode())
                decrypted_data = self._fernet.decrypt(encrypted_data)
                license_data = json.loads(decrypted_data.decode())
            except Exception as e:
                return {
                    "valid": False,
                    "error": "Invalid license key format"
                }
            
            # Validate required fields
            required_fields = ["user_email", "expires", "features", "license_type"]
            for field in required_fields:
                if field not in license_data:
                    return {
                        "valid": False,
                        "error": f"License missing required field: {field}"
                    }
            
            # Validate expiration
            try:
                expires_str = license_data["expires"]
                expires_date = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                if expires_date < datetime.now():
                    return {
                        "valid": False,
                        "error": "License has expired"
                    }
            except Exception as e:
                return {
                    "valid": False,
                    "error": "Invalid license expiration date"
                }
            
            # Validate email format (basic check)
            email = license_data["user_email"]
            if "@" not in email or "." not in email:
                return {
                    "valid": False,
                    "error": "Invalid email format in license"
                }
            
            return {
                "valid": True,
                "license_info": license_data
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"License validation error: {str(e)}"
            }

    def _format_license_key(self, license_key: str) -> str:
        """Format license key for display (keep full key for functionality)"""
        # For functionality, we need the full key, so don't truncate
        # Just return the full key - the UI can display it nicely
        return license_key

    async def get_status(self) -> Dict[str, Any]:
        """Get provider status (required by BaseProvider)"""
        try:
            # Test keychain access
            test_result = keyring.get_password("apex-test", "test")
            
            return {
                "success": True,
                "provider": "license",
                "status": "healthy",
                "keychain_available": True,
                "message": "License provider ready"
            }
        except Exception as e:
            return {
                "success": False,
                "provider": "license",
                "status": "error",
                "keychain_available": False,
                "error": str(e)
            }

    async def validate_license_key(self, license_key: str) -> Dict[str, Any]:
        """Public method to validate a license key without activating it"""
        return await self._validate_license_key(license_key)

    async def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Authenticate using current license (required by BaseProvider)"""
        return await self.get_license_status()
