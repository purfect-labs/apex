#!/usr/bin/env python3
"""
APEX License Validation System
User-based license key validation with macOS Keychain integration
No backend server required - all validation is offline/local
"""

import hashlib
import hmac
import json
import platform
import socket
import subprocess
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class APEXLicenseManager:
    """Secure license validation for APEX application"""
    
    APP_NAME = "APEX"
    LICENSE_SERVICE = "apex-license"
    MASTER_KEY = b"apex_master_key_2024"  # In production, this should be more secure
    
    def __init__(self):
        self.cipher = self._initialize_cipher()
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize Fernet cipher with application key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'apex_app_salt_2024',  # Fixed salt for consistency
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.MASTER_KEY))
        return Fernet(key)
    
    def _validate_user_info(self, license_data: Dict) -> bool:
        """Validate user information in license"""
        # Check if license has required user info
        required_fields = ['user_email']
        
        for field in required_fields:
            if field not in license_data:
                return False
        
        # Validate email format (basic check)
        email = license_data.get('user_email', '')
        if '@' not in email or '.' not in email:
            return False
            
        return True
    
    def validate_license_key(self, license_key: str) -> Dict[str, any]:
        """Validate a license key against user information"""
        try:
            # Decode and decrypt license
            license_data = self._decode_license_key(license_key)
            
            if not license_data:
                return {"valid": False, "error": "Invalid license format"}
            
            # Validate user information
            if not self._validate_user_info(license_data):
                return {"valid": False, "error": "Invalid user information in license"}
            
            # Check expiration
            if 'expires' in license_data:
                expiry_date = datetime.fromisoformat(license_data['expires'])
                if datetime.now() > expiry_date:
                    return {"valid": False, "error": "License has expired"}
            
            # Check feature flags
            features = license_data.get('features', [])
            user_email = license_data.get('user_email')
            user_name = license_data.get('user_name', user_email.split('@')[0] if user_email else 'Licensed User')
            
            return {
                "valid": True,
                "user_name": user_name,
                "user_email": user_email,
                "expires": license_data.get('expires'),
                "features": features,
                "license_type": license_data.get('license_type', 'standard')
            }
            
        except Exception as e:
            return {"valid": False, "error": f"License validation error: {str(e)}"}
    
    def _decode_license_key(self, license_key: str) -> Optional[Dict]:
        """Decode and decrypt license key"""
        try:
            # Remove any whitespace and dashes
            clean_key = license_key.replace('-', '').replace(' ', '').strip()
            
            # Base64 decode
            encrypted_data = base64.urlsafe_b64decode(clean_key.encode())
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Parse JSON
            return json.loads(decrypted_data.decode())
            
        except Exception:
            return None
    
    def store_license(self, license_key: str) -> bool:
        """Store valid license in macOS Keychain"""
        try:
            validation = self.validate_license_key(license_key)
            if validation["valid"]:
                keyring.set_password(self.LICENSE_SERVICE, self.APP_NAME, license_key)
                return True
            return False
        except Exception:
            return False
    
    def load_stored_license(self) -> Optional[Dict[str, any]]:
        """Load and validate stored license from Keychain"""
        try:
            stored_key = keyring.get_password(self.LICENSE_SERVICE, self.APP_NAME)
            if stored_key:
                return self.validate_license_key(stored_key)
            return None
        except Exception:
            return None
    
    def clear_stored_license(self) -> bool:
        """Remove stored license from Keychain"""
        try:
            keyring.delete_password(self.LICENSE_SERVICE, self.APP_NAME)
            return True
        except Exception:
            return False
    
    def generate_trial_license(self, user_email: str = None, days: int = 30) -> str:
        """Generate a trial license for user (development/testing only)"""
        try:
            if not user_email:
                user_email = "trial@example.com"
            
            trial_data = {
                'user_name': 'Trial User',
                'user_email': user_email,
                'expires': (datetime.now() + timedelta(days=days)).isoformat(),
                'features': ['basic'],
                'license_type': 'trial',
                'issued': datetime.now().isoformat()
            }
            
            # Encrypt and encode
            encrypted_data = self.cipher.encrypt(json.dumps(trial_data).encode())
            license_key = base64.urlsafe_b64encode(encrypted_data).decode()
            
            # Format with dashes for readability
            formatted_key = '-'.join([license_key[i:i+4] for i in range(0, len(license_key), 4)])
            return formatted_key
            
        except Exception as e:
            raise Exception(f"Failed to generate trial license: {str(e)}")
    
    def get_machine_info(self) -> Dict[str, str]:
        """Get machine information for reference"""
        return {
            'platform': platform.system(),
            'machine': platform.machine(),
            'hostname': socket.gethostname(),
            'python_version': platform.python_version()
        }
    
    def generate_license_key(self, user_email: str, user_name: str = None, 
                           days_valid: int = 365, features: list = None) -> str:
        """Generate a license key for a user (for license generation)"""
        try:
            if not user_name:
                user_name = user_email.split('@')[0].title()
            
            if not features:
                features = ['basic']
            
            license_data = {
                'user_name': user_name,
                'user_email': user_email,
                'expires': (datetime.now() + timedelta(days=days_valid)).isoformat(),
                'features': features,
                'license_type': 'standard',
                'issued': datetime.now().isoformat()
            }
            
            # Encrypt and encode
            encrypted_data = self.cipher.encrypt(json.dumps(license_data).encode())
            license_key = base64.urlsafe_b64encode(encrypted_data).decode()
            
            # Format with dashes for readability
            formatted_key = '-'.join([license_key[i:i+4] for i in range(0, len(license_key), 4)])
            return formatted_key
            
        except Exception as e:
            raise Exception(f"Failed to generate license key: {str(e)}")


def check_license() -> Tuple[bool, Optional[Dict]]:
    """Main license check function for application startup"""
    manager = APEXLicenseManager()
    
    # Try to load stored license first
    license_info = manager.load_stored_license()
    
    if license_info and license_info["valid"]:
        return True, license_info
    
    return False, None


def prompt_for_license() -> Tuple[bool, Optional[Dict]]:
    """Prompt user for license key (command line version)"""
    manager = APEXLicenseManager()
    
    print("\n" + "="*60)
    print("🔐 APEX License Activation Required")
    print("="*60)
    print("\nAPEX requires a valid license to run.")
    print("This is a user-based license system (no backend required).")
    
    print("\nOptions:")
    print("1. Enter license key")
    print("2. Generate trial license (30 days)")
    print("3. Generate custom license")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            license_key = input("\nEnter your license key: ").strip()
            if license_key:
                validation = manager.validate_license_key(license_key)
                if validation["valid"]:
                    if manager.store_license(license_key):
                        print(f"\n\u2705 License activated successfully!")
                        print(f"User: {validation['user_name']} ({validation['user_email']})")
                        if validation.get('expires'):
                            print(f"Expires: {validation['expires']}")
                        return True, validation
                    else:
                        print("❌ Failed to store license")
                else:
                    print(f"❌ License validation failed: {validation['error']}")
            else:
                print("❌ No license key entered")
                
        elif choice == "2":
            try:
                trial_key = manager.generate_trial_license()
                validation = manager.validate_license_key(trial_key)
                if manager.store_license(trial_key):
                    print(f"\n✅ Trial license generated and activated!")
                    print(f"Expires: {validation['expires']}")
                    return True, validation
                else:
                    print("❌ Failed to store trial license")
            except Exception as e:
                print(f"❌ Failed to generate trial license: {e}")
                
        elif choice == "3":
            return False, None
        
        else:
            print("❌ Invalid option, please select 1, 2, or 3")


if __name__ == "__main__":
    # Command line testing
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "info":
            manager = APEXLicenseManager()
            info = manager.get_machine_info()
            print("Machine Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        elif sys.argv[1] == "trial":
            manager = APEXLicenseManager()
            trial_key = manager.generate_trial_license()
            print(f"Trial License Key: {trial_key}")
            
        elif sys.argv[1] == "validate":
            if len(sys.argv) > 2:
                manager = APEXLicenseManager()
                result = manager.validate_license_key(sys.argv[2])
                print(f"Validation Result: {result}")
            else:
                print("Usage: python apex_license.py validate <license_key>")
    else:
        # Interactive mode
        success, info = prompt_for_license()
        if success:
            print(f"\n🚀 License validated! Application can now start.")
        else:
            print("\n❌ License validation failed. Exiting.")
            sys.exit(1)