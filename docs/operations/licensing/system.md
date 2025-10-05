# License Management System Documentation

## Overview

The APEX License Management System provides comprehensive license operations through the `LicenseProvider` class, integrating with system keychain for secure storage and featuring encrypted license key generation with validation mechanisms.

**File Location**: `web/providers/license.py`  
**Provider Pattern**: Extends `BaseProvider` following APEX architecture  
**Security**: Uses Fernet encryption with keychain integration  
**Storage**: System keychain via `keyring` library

## LicenseProvider Class Architecture

### Class Initialization

```python
class LicenseProvider(BaseProvider):
    """License operations provider with keychain integration"""
    
    def __init__(self):
        super().__init__("license")
        # Fixed demo encryption key - for production use proper key management
        self._demo_key = base64.urlsafe_b64encode(b"apex_demo_license_key_32_chars_!").decode()
        self._fernet = Fernet(self._demo_key.encode())
        self._keychain_service = "apex-license"
        self._keychain_account = "APEX"
```

**Initialization Features**:
- ✅ **Demo Encryption Key**: Uses fixed 32-character demo key for testing
- ✅ **Fernet Encryption**: Symmetric encryption for license data
- ✅ **Keychain Integration**: Secure storage via system keychain
- ✅ **Service Identification**: "apex-license" service with "APEX" account

### Core License Operations

## License Status Management

### Get License Status

```python
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
```

**Status Management Features**:
- ✅ **Keychain Retrieval**: Secure license key retrieval from system keychain
- ✅ **Automatic Validation**: Validates stored license on every status check
- ✅ **Auto-Cleanup**: Removes invalid licenses automatically
- ✅ **Expiration Calculation**: Real-time days remaining calculation
- ✅ **Comprehensive Response**: Returns all license details or clear error states

### License Activation

```python
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
```

**Activation Features**:
- ✅ **Pre-Validation**: Validates license before activation
- ✅ **Email Verification**: Optional email matching for additional security
- ✅ **Secure Storage**: Stores in system keychain after validation
- ✅ **Detailed Response**: Returns all license information on successful activation

### License Deactivation

```python
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
```

**Deactivation Features**:
- ✅ **Clean Removal**: Completely removes license from keychain
- ✅ **Graceful Handling**: Handles case where no license exists
- ✅ **Error Recovery**: Detailed error reporting for debugging

## License Generation System

### Trial License Generation

```python
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
```

**Trial License Features**:
- ✅ **Automatic Expiration**: Configurable trial period (default 7 days)
- ✅ **Basic Features**: Trial licenses include basic feature set
- ✅ **Email-Based Names**: Automatically generates user name from email
- ✅ **Full Encryption**: Uses same security as full licenses
- ✅ **Generation Timestamp**: Records creation time for auditing

### Full License Generation

```python
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
```

**Full License Features**:
- ✅ **Custom Duration**: Configurable license period
- ✅ **Feature Control**: Specify exact feature set for license
- ✅ **Custom User Names**: Accept provided user name instead of generating
- ✅ **Standard Type**: Full licenses marked as "standard" type
- ✅ **Complete Metadata**: Records all generation parameters

## License Validation System

### Core Validation Logic

```python
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
```

**Validation Features**:
- ✅ **Format Flexibility**: Handles formatted (XXXX-XXXX-XXXX-XXXX) and raw license keys
- ✅ **Encryption Verification**: Validates proper decryption with demo key
- ✅ **Field Validation**: Ensures all required fields present
- ✅ **Expiration Checking**: Real-time expiration validation
- ✅ **Email Verification**: Basic email format validation
- ✅ **Comprehensive Error Messages**: Detailed error reporting for debugging

## WARP Demo License Examples

### Demo License Data Structures

```python
# WARP FAKE DEMO license examples for testing and documentation

WARP_DEMO_LICENSES = {
    "trial_user": {
        "user_email": "warp-demo-user@warp-test.com",
        "user_name": "WARP Demo User", 
        "license_key": "WARP-DEMO-TRIAL-1111-2222-3333-4444",
        "license_type": "trial",
        "days_remaining": 7,
        "features": ["basic"],
        "expires": "2024-12-31T23:59:59Z",
        "status": "active"
    },
    "standard_user": {
        "user_email": "warp-standard@warp-test.com",
        "user_name": "WARP Standard Demo",
        "license_key": "WARP-STD-DEMO-AAAA-BBBB-CCCC-DDDD", 
        "license_type": "standard",
        "days_remaining": 365,
        "features": ["basic", "advanced", "premium"],
        "expires": "2025-12-31T23:59:59Z",
        "status": "active"
    },
    "expired_user": {
        "user_email": "warp-expired@warp-test.com",
        "user_name": "WARP Expired Demo",
        "license_key": "WARP-EXP-DEMO-9999-8888-7777-6666",
        "license_type": "trial", 
        "days_remaining": -5,
        "features": [],
        "expires": "2023-01-01T00:00:00Z",
        "status": "expired"
    }
}
```

### Demo Response Examples

**License Status Response (Active)**:
```json
{
    "success": true,
    "status": "active",
    "message": "License is active",
    "user_email": "warp-demo-user@warp-test.com",
    "user_name": "WARP Demo User",
    "expires": "2024-12-31T23:59:59Z",
    "features": ["basic"],
    "license_type": "trial",
    "days_remaining": 30
}
```

**License Status Response (Inactive)**:
```json
{
    "success": true,
    "status": "inactive",
    "message": "No license found",
    "user_email": null,
    "expires": null,
    "features": [],
    "license_type": null,
    "days_remaining": null
}
```

**Trial License Generation Response**:
```json
{
    "success": true,
    "license_key": "WARP-DEMO-TRIAL-1111-2222-3333-4444",
    "user_email": "warp-demo-user@warp-test.com",
    "expires": "2024-01-15T10:30:00Z",
    "days": 7,
    "message": "7-day trial license generated successfully"
}
```

**License Activation Response**:
```json
{
    "success": true,
    "message": "License activated successfully",
    "user_email": "warp-demo-user@warp-test.com",
    "user_name": "WARP Demo User",
    "expires": "2024-12-31T23:59:59Z",
    "features": ["basic"],
    "license_type": "trial"
}
```

### Demo Error Scenarios

**Invalid License Key Error**:
```json
{
    "success": false,
    "error": "Invalid license key format"
}
```

**Expired License Error**:
```json
{
    "success": true,
    "status": "invalid",
    "message": "License has expired",
    "user_email": null,
    "expires": null,
    "features": [],
    "license_type": null,
    "days_remaining": null
}
```

**Email Mismatch Error**:
```json
{
    "success": false,
    "error": "License key does not match email warp-wrong-user@warp-test.com"
}
```

## Provider Integration Patterns

### BaseProvider Implementation

```python
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

async def authenticate(self, **kwargs) -> Dict[str, Any]:
    """Authenticate using current license (required by BaseProvider)"""
    return await self.get_license_status()
```

**Integration Features**:
- ✅ **BaseProvider Compliance**: Implements required `get_status()` and `authenticate()` methods
- ✅ **Health Checking**: Tests keychain availability on status requests
- ✅ **Authentication Bridge**: Maps authenticate calls to license status checks
- ✅ **Provider Registry**: Integrates with APEX provider registry system

## Security Implementation

### Encryption System

**Demo Encryption Key**:
```python
# Fixed demo encryption key - for production use proper key management
self._demo_key = base64.urlsafe_b64encode(b"apex_demo_license_key_32_chars_!").decode()
self._fernet = Fernet(self._demo_key.encode())
```

**Security Features**:
- ✅ **Fernet Encryption**: Symmetric encryption using cryptography library
- ✅ **32-Character Key**: Properly sized encryption key for security
- ✅ **Base64 Encoding**: URL-safe encoding for license key transport
- ✅ **Demo Warning**: Clear indication this is demo key, not production

### Keychain Integration

**Keychain Configuration**:
```python
self._keychain_service = "apex-license"
self._keychain_account = "APEX"
```

**Keychain Features**:
- ✅ **System Integration**: Uses OS keychain (Keychain Access on macOS)
- ✅ **Service Isolation**: Dedicated "apex-license" service identifier
- ✅ **Account Organization**: Single "APEX" account for all license operations
- ✅ **Secure Storage**: Encrypted storage managed by operating system

## Usage Patterns and API Integration

### Controller Integration

The LicenseProvider integrates with `web/controllers/license_controller.py`:

```python
# Example controller usage
license_provider = provider_registry.get_provider("license")

# Check current license status
status = await license_provider.get_license_status()

# Activate a new license
activation = await license_provider.activate_license(
    license_key="WARP-DEMO-TRIAL-1111-2222-3333-4444",
    user_email="warp-demo-user@warp-test.com"
)

# Generate trial license
trial = await license_provider.generate_trial_license(
    user_email="warp-demo-user@warp-test.com",
    days=7
)
```

### API Endpoint Integration

**License Management Endpoints**:
- `GET /api/license/status` → `get_license_status()`
- `POST /api/license/activate` → `activate_license()`  
- `POST /api/license/deactivate` → `deactivate_license()`
- `POST /api/license/generate-trial` → `generate_trial_license()`
- `POST /api/license/generate-full` → `generate_full_license()`

### WebSocket Integration

License operations support real-time updates via WebSocket broadcasting:

```python
# License activation with broadcasting
await self.broadcast_message({
    "type": "license_activated", 
    "user_email": "warp-demo-user@warp-test.com",
    "features": ["basic"],
    "expires": "2024-12-31T23:59:59Z"
})

# License status changes
await self.broadcast_message({
    "type": "license_status_changed",
    "status": "expired",
    "message": "License has expired"
})
```

## Testing and Development

### Local Development Setup

**Required Dependencies**:
```python
# requirements.txt entries
keyring>=24.0.0
cryptography>=41.0.0
```

**Development Testing**:
```bash
# Test license provider functionality
python3 -c "
from web.providers.license import LicenseProvider
import asyncio

async def test_license():
    provider = LicenseProvider()
    
    # Generate demo trial license
    trial = await provider.generate_trial_license('warp-demo@warp-test.com', 7)
    print('Trial License:', trial)
    
    # Test license validation
    if trial['success']:
        validation = await provider.validate_license_key(trial['license_key'])
        print('Validation:', validation)

asyncio.run(test_license())
"
```

### Error Handling Patterns

**Comprehensive Error Responses**:
- **Keychain Errors**: Handles keychain access failures gracefully
- **Encryption Errors**: Catches decryption failures with clear messages  
- **Validation Errors**: Specific error messages for each validation failure
- **Format Errors**: Handles malformed license keys and data structures
- **Network Errors**: Graceful handling of system-level failures

This License Management System provides complete license lifecycle management with secure keychain integration, encrypted license generation, comprehensive validation, and full APEX provider pattern compliance. All examples use WARP demo data to avoid confusion with real license information.

<citations>
<document>
    <document_type>RULE</document_type>
    <document_id>DdzrPTuR904KjfjPhIj8gG</document_id>
</document>
<document>
    <document_type>RULE</document_type>
    <document_id>asIO3B744xXFjLwhR7suHb</document_id>
</document>
</citations>