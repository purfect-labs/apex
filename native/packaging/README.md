# APEX macOS Installer - Complete Guide

## Overview

This system creates a professional macOS installer for your APEX application with:
- ✅ **User-based licensing** (email-bound, no hardware locking)
- ✅ **Native macOS app** (`.app` bundle with PyWebView)
- ✅ **Single-file distribution** (DMG installer)
- ✅ **Embedded web assets** (HTML/CSS/JS bundled into executable)
- ✅ **License validation** (stored securely in macOS Keychain)
- ✅ **Professional packaging** (Code signing ready)

## Quick Start

### 1. Build the Installer

```bash
# Install dependencies
pip install -r requirements.txt

# Build everything (DMG installer, license system, etc.)
./build_installer.sh
```

### 2. Generate License Keys

```bash
# Interactive license generation
python3 generate_license.py

# Batch license generation
python3 generate_license.py batch "user@company.com" "John Doe" 365 basic,advanced
```

### 3. Distribute

- Share the DMG file from `dist/APEX-3.0.0-macOS.dmg`
- Provide license keys to users
- Users drag the app to Applications folder

## File Structure

```
apex/
├── apex_app.py              # Native macOS application (main entry point)
├── apex_license.py          # License validation system
├── apex_resources.py        # Web asset bundling system
├── generate_license.py      # License key generator
├── apex.spec               # PyInstaller configuration
├── build_installer.sh      # Complete build script
├── requirements.txt        # Python dependencies
└── dist/                   # Output directory
    ├── APEX.app            # macOS application bundle
    ├── APEX-3.0.0-macOS.dmg # DMG installer
    └── README.txt          # Distribution documentation
```

## License System Details

### How It Works
1. **No Backend Required** - All validation is local/offline
2. **User-Based** - License tied to email address, works on multiple machines
3. **Encrypted Storage** - License keys stored securely in macOS Keychain
4. **Feature Flags** - Support different license tiers (basic, advanced, premium)

### License Key Format
```json
{
  "user_email": "user@company.com",
  "user_name": "John Doe",
  "expires": "2025-12-31T23:59:59",
  "features": ["basic", "advanced"],
  "license_type": "standard"
}
```
*↳ This is encrypted and base64-encoded into the license key*

### License Management Commands

```bash
# Generate trial license (30 days)
python3 apex_license.py trial

# Validate existing license
python3 apex_license.py validate "XXXX-XXXX-XXXX-XXXX"

# Get machine info
python3 apex_license.py info

# Interactive license activation
python3 apex_license.py
```

## Application Modes

### Native App Mode (Default)
```bash
# Runs in native macOS window
python3 apex_app.py
```

### Browser Mode
```bash
# Opens in default browser
python3 apex_app.py --browser
```

### License Management Mode
```bash
# Manage licenses without starting app
python3 apex_app.py --license
```

## Customization

### Update App Information
Edit these files:
- `apex.spec` - App name, version, bundle ID
- `build_installer.sh` - Version numbers, developer ID
- `apex_app.py` - Application title, window size

### Add App Icon
1. Create icon files (16x16 to 1024x1024 PNG)
2. Convert to `.icns`: `iconutil -c icns icon.iconset`
3. Place in `assets/icon.icns`

### Customize License Terms
Edit the license text in `build_installer.sh` (search for "LICENSE AGREEMENT")

## Code Signing & Notarization

### Requirements
- Apple Developer Account ($99/year)
- Developer ID Application certificate

### Setup
1. Get your Developer ID:
   ```bash
   security find-identity -v -p codesigning
   ```

2. Set environment variable:
   ```bash
   export DEVELOPER_ID="Developer ID Application: Your Name (TEAMID)"
   ```

3. Build with signing:
   ```bash
   ./build_installer.sh
   ```

### Notarization (Optional but Recommended)
```bash
# After building, submit for notarization
xcrun notarytool submit dist/APEX-3.0.0-macOS.dmg \
  --apple-id "your@email.com" \
  --team-id "TEAMID" \
  --password "app-specific-password"

# Check status
xcrun notarytool info <submission-id> \
  --apple-id "your@email.com" \
  --team-id "TEAMID" \
  --password "app-specific-password"

# Staple ticket to DMG
xcrun stapler staple dist/APEX-3.0.0-macOS.dmg
```

## Distribution Workflow

### For Developers
1. **Build**: Run `./build_installer.sh`
2. **Test**: Install DMG on clean macOS system
3. **Sign**: Configure code signing (optional)
4. **Distribute**: Share DMG file

### For Users
1. **Download**: Get the DMG file
2. **Install**: Open DMG, drag app to Applications
3. **License**: Enter license key when prompted
4. **Use**: Launch from Applications or Launchpad

## Security Features

### License Protection
- ✅ **Encrypted license keys** using Fernet encryption
- ✅ **Secure storage** in macOS Keychain
- ✅ **Email validation** (basic format checking)
- ✅ **Expiration checking** with ISO date formats
- ✅ **Feature flags** for different license tiers

### Code Protection
- ✅ **Bytecode compilation** (Python `.pyc` files)
- ✅ **Resource embedding** (HTML/CSS/JS not accessible as files)
- ✅ **Single executable** (harder to modify)
- ✅ **Code signing** support (when configured)

## Troubleshooting

### Build Issues
```bash
# Clean build
rm -rf build dist
./build_installer.sh

# Check dependencies
pip install -r requirements.txt --upgrade

# Debug PyInstaller
pyinstaller apex.spec --clean --debug all
```

### License Issues
```bash
# Clear stored license
python3 -c "
import keyring
keyring.delete_password('apex-license', 'APEX')
print('License cleared')
"

# Test license generation
python3 generate_license.py
```

### Runtime Issues
```bash
# Run in browser mode for debugging
python3 apex_app.py --browser

# Check logs
tail -f apex.log
```

## Development vs Production

### Development Mode
- Uses file system resources (web/ directory)
- Console logging enabled
- No code signing required
- Debug mode available

### Production Mode
- Embedded resources (bundled into executable)
- Minimal logging
- Code signing recommended
- Optimized executable

## Advanced Configuration

### Custom License Validation
Modify `_validate_user_info()` in `apex_license.py`:

```python
def _validate_user_info(self, license_data: Dict) -> bool:
    """Custom license validation logic"""
    # Add your custom validation here
    email = license_data.get('user_email', '')
    
    # Example: Only allow company emails
    if not email.endswith('@yourcompany.com'):
        return False
    
    return True
```

### Custom Features
Add feature flags in license generation:

```python
# Generate license with specific features
license_key = manager.generate_license_key(
    user_email="user@company.com",
    user_name="John Doe", 
    days_valid=365,
    features=["basic", "advanced", "database_access", "admin_panel"]
)
```

Then check features in your app:
```python
if 'database_access' in self.license_info.get('features', []):
    # Enable database functionality
    pass
```

## Support

### Common Issues
- **"App is damaged"**: Enable code signing or disable Gatekeeper temporarily
- **License not found**: Check macOS Keychain Access app
- **Build fails**: Ensure all dependencies installed with `pip install -r requirements.txt`

### Debug Mode
```bash
# Enable debug logging
export APEX_DEBUG=1
python3 apex_app.py
```

---

## Summary

You now have a complete macOS installer system that provides:

1. **Professional Distribution** - DMG installer with license agreement
2. **User-Based Licensing** - Email-bound licenses (no backend required)
3. **Native Experience** - True macOS app with PyWebView
4. **Security** - Encrypted licenses, code signing support
5. **Easy Management** - Simple license generation and validation tools

The system is production-ready and includes all the components needed for commercial software distribution on macOS.