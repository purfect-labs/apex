# WARP.md - APEX Cloud Operations Command Center

This file provides guidance to WARP (warp.dev) when working with the APEX codebase - a three-tier cloud operations command center supporting AWS, GCP, and Kubernetes integration.

## 🔍 Codebase Understanding First Steps

**ALWAYS start by understanding the full codebase using the llm-collector tool:**

```bash
python3 llm-collector/run.py  # Generates flat JSON of all git-tracked files
```

This generates `llm-collector/results.json` (154 files, 41,853 lines) containing the complete codebase flattened into a single JSON file. Always read this first to understand the full architecture before making any changes.

## 📊 Current System Stats
- **Total Files**: 154 (45 Python, 36 JavaScript, 13 CSS, 12 HTML)
- **Lines of Code**: 41,853
- **Architecture**: Four-tier (Routes → Controllers → Providers → External APIs)
- **Supported Services**: AWS, GCP, Kubernetes, Database tunneling
- **Real-time Features**: WebSocket streaming, live command output
- **Deployment**: Web server + Native desktop (Electron)

## Common Development Commands

### Build Commands

```bash
# Complete DMG build (native macOS app)
./build.sh                    # Full build with embedded resources
./build.sh --open             # Build and auto-open DMG

# Alternative build methods
python3 build_apex.py         # Controlled build script
python3 build_apex.py --clean-only  # Clean cache only
python3 build_apex.py --status      # Check build system

# Manual build steps (for debugging)
python3 build_resources.py    # Create embedded web resources
pyinstaller apex.spec --clean # Build native executable
```

### Development Server Commands

```bash
# Web development mode
python3 web/main.py           # Direct FastAPI server (port 8000)

# Native desktop mode
python3 apex_app.py           # Native macOS window with PyWebView
python3 apex_app.py --browser # Opens in default browser
python3 apex_app.py --license # License management mode

# Electron development
cd electron && npm start      # Electron wrapper development
```

### Testing Commands

**CRITICAL: Follow multi-layer testing approach - always validate with multiple methods:**

```bash
# 1. End-to-end Playwright tests (real user flows with native events)
npx playwright test tests/auth-test.spec.js

# 2. Integration tests - curl API endpoints directly  
curl -X POST http://localhost:8000/api/auth -H "Content-Type: application/json" -d '{"provider":"aws","profile":"dev"}'
curl -X GET http://localhost:8000/api/status

# 3. HTML source validation with wget
wget -qO- http://localhost:8000 > page.html  # Validate actual HTML output

# 4. WebSocket testing
# Test WebSocket connections manually using browser dev tools or wscat
```

**Background testing for long-running processes (use tmp logging):**

```bash
# Use backgrounding and tmp logging for tests that might block or fail
nohup playwright test --headed > /tmp/test-$(date +%s).log 2>&1 &
tail -f /tmp/test-*.log  # Monitor progress

# For database connection tests
timeout 30s ./bin/start-all-db-connections.sh > /tmp/db-test.log 2>&1 || echo "DB test timed out"
```

### Configuration Setup

```bash
# AWS SSO configuration setup
./bin/setup-aws-sso-auth.sh      # Interactive SSO role setup
./bin/setup-aws-db-config.sh     # Database username configuration  
./bin/config-setup.sh            # Complete configuration setup

# Manual configuration check
aws sts get-caller-identity --profile dev    # Test AWS auth
gcloud auth list                             # Test GCP auth
kubectl get pods                            # Test Kubernetes access
```

## Architecture Overview

APEX is a **three-tier cloud operations command center** with sophisticated abstraction patterns:

### System Architecture

- **Entry Points**: 
  - `web/main.py` → Web server mode (FastAPI)
  - `apex_app.py` → Native desktop mode (PyWebView)
  - `electron/main.js` → Electron wrapper
  
- **Four-Tier Pattern**:
  1. **Routes** (`web/routes/`) → HTTP endpoint definitions & request handling
  2. **Controllers** (`web/controllers/`) → Business logic orchestration
  3. **Providers** (`web/providers/`) → Direct CLI/API integration  
  4. **External APIs** → AWS CLI, gcloud, kubectl, etc.

### Key Architectural Patterns

- **Registry Pattern**: Centralized service discovery (`ControllerRegistry`, `ProviderRegistry`)
- **Template Method**: Base classes with standardized interfaces (`BaseController`, `BaseProvider`)
- **Environment Abstraction**: UI uses `dev/stage/prod`, maps to actual AWS profiles/GCP projects
- **Real-time Communication**: WebSocket streaming for live command output
- **Configuration as Code**: Environment-agnostic YAML/INI configuration

### Core File Structure

```
apex/
├── web/                     # Main web application
│   ├── main.py             # FastAPI server entry point
│   ├── routes/             # HTTP API endpoint definitions
│   │   ├── aws/           # AWS-specific routes (auth, commands, resources)
│   │   ├── gcp/           # GCP-specific routes  
│   │   └── k8s/           # Kubernetes-specific routes
│   ├── controllers/        # Business logic layer
│   ├── providers/          # Integration layer (AWS, GCP, K8s)
│   ├── static/js/          # Frontend JavaScript components
│   └── templates/          # HTML templates
├── config/                 # Configuration management
│   ├── static/            # Static config templates
│   └── *.config           # Rendered environment configs
├── electron/              # Desktop application wrapper
├── tests/                 # Playwright end-to-end tests
├── llm-collector/         # Codebase analysis tool
└── docs/                  # Architecture documentation
```

## Development Guidelines & Conventions

### Import Management
**ALWAYS add imports to the top of files, never inside methods or functions.**

```python
# ✅ CORRECT - Top of file
import asyncio
from pathlib import Path
from web.providers.aws.auth import AWSAuth

def my_function():
    # Use imports here
```

### Configuration and Environment Handling

**DON'T hardcode environments, layers, or configurations. Always consume config and stay agnostic:**

```python
# ✅ CORRECT - Use configuration abstraction
env = request.env or "dev"
aws_profile = get_aws_profile_for_env(env)  # Maps to actual profile
gcp_project = get_gcp_project_for_env(env)  # Maps to actual project

# ❌ WRONG - Hardcoded values
aws_profile = "my-dev-profile"  # DON'T do this
```

**DON'T reinitialize configs or use sys calls for configuration unless it's one-time initial setup:**

```python
# ✅ CORRECT - Use global config instance
config = get_config()  # Singleton, initialized once

# ❌ WRONG - Multiple config initialization
config = APEXConfigLoader()  # Don't create new instances
```

### Issue Fixing Strategy

**Fix lightweight issues concurrently, heavy issues one at a time:**

**Lightweight Issues (Fix concurrently):**
- Missing controller methods (simple additions)
- Request parameter mapping fixes
- Return format changes
- Route endpoint corrections

**Heavy Issues (Fix one at a time):**
- Complete provider rewrites
- Major API schema changes
- Authentication system overhauls
- Database schema modifications

### Multi-Layer Validation Strategy

**ALWAYS doubt your code is working. Implement multiple validation layers:**

1. **Playwright Tests** - User flows with native events
2. **Direct API Testing** - curl to endpoints  
3. **Source Validation** - wget to get actual HTML
4. **Manual Verification** - Test in real browsers

```python
# Example validation pattern in providers
async def authenticate(self, **kwargs):
    # Execute command
    result = await self.execute_command("aws sso login --profile dev")
    
    # Multiple validation layers
    if result['success']:
        # Layer 1: Verify with another command
        verify = await self.execute_command("aws sts get-caller-identity --profile dev")
        
        # Layer 2: Check actual response content
        if "Account" in verify.get('stdout', ''):
            # Layer 3: Broadcast for real-time validation
            await self.broadcast_message({'type': 'auth_success'})
        else:
            return {'success': False, 'error': 'Verification failed'}
    
    return result
```

### Command Execution Patterns

**Use backgrounding and tmp logging for commands that might block or fail:**

```python
# For potentially blocking operations
async def risky_operation(self):
    # Use timeout and background logging
    try:
        result = await asyncio.wait_for(
            self.execute_command("long-running-command"),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        # Log to tmp file for debugging
        with open(f'/tmp/apex-error-{int(time.time())}.log', 'w') as f:
            f.write(f"Operation timed out: {command}\n")
        return {'success': False, 'error': 'Operation timed out'}
```

## Routes Layer (HTTP API Endpoints)

### Current Route Structure

**AWS Routes** (`web/routes/aws/`):
- `auth.py` - AWS authentication endpoints (`/api/aws/auth`, `/api/aws/status`, `/api/aws/profiles`)
- `commands.py` - AWS command execution (`/api/aws/execute`, `/api/aws/switch-profile`)
- `resources.py` - AWS resource management (`/api/aws/resources`, `/api/aws/endpoints`)

**GCP Routes** (planned: `web/routes/gcp/`):
- `auth.py` - GCP authentication endpoints
- `commands.py` - GCP command execution
- `k8s.py` - Kubernetes-specific endpoints

### Route → Controller → Provider Flow

```python
# Example: /api/aws/identity endpoint
@app.get("/api/aws/identity")
async def aws_identity(env: str = "dev"):
    """Route: HTTP request handling"""
    aws_controller = controller_registry.get_aws_controller()
    
    if aws_controller:
        return await aws_controller.get_current_identity(env=env)  # Controller: Business logic
    else:
        return {"success": False, "error": "AWS controller not available"}

# Controller calls Provider:
# aws_controller.get_current_identity() → aws_auth.get_profile_status() → aws sts get-caller-identity
```

### Standard Route Patterns

**Authentication Routes**:
- `POST /api/{service}/auth` - Service authentication
- `GET /api/{service}/status` - Service status check
- `GET /api/{service}/profiles` - List available profiles/projects

**Command Routes**:
- `POST /api/{service}/execute` - Execute service-specific commands  
- `POST /api/{service}/switch-profile` - Switch profiles/contexts

**Resource Routes**:
- `GET /api/{service}/resources` - List service resources
- `GET /api/{service}/endpoints` - Discover available endpoints

## Provider Integration Patterns

### Adding New Service Integrations

1. **Create Routes** (`web/routes/{service}/`) - HTTP endpoint definitions
2. **Create Controller** (`web/controllers/{service}_controller.py`) - Business logic
3. **Create Provider** (`web/providers/{service}/operations.py`) - CLI integration
4. **Register Components** (in `web/main.py`) - Wire up dependencies
5. **Add Frontend Integration** - UI components and JavaScript

### Standard Provider Interface

```python
class ServiceProvider(BaseProvider):
    async def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Required: Service-specific authentication"""
        
    async def get_status(self) -> Dict[str, Any]:
        """Required: Health/status check"""
        
    async def execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Inherited: Standardized command execution with real-time streaming"""
```

## Real-time Communication

All command execution streams output via WebSocket:

```javascript
// Frontend receives real-time updates
ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    if (message.type === 'command_output') {
        addTerminalLine('Output', message.data.output);
    }
};
```

## Cloud Service Integration

### Current Integrations

- **AWS**: SSO authentication, profile management, RDS connections
- **GCP**: Authentication, project management, Kubernetes clusters
- **Kubernetes**: Pod management, Kiali port forwarding
- **Database**: Multi-environment connection tunneling

### Command Examples

```bash
# AWS operations
aws sso login --profile dev
aws sts get-caller-identity --profile dev

# GCP operations
gcloud auth login --no-launch-browser
gcloud config set project kenect-service-dev

# Kubernetes operations
gcloud container clusters get-credentials dev-cluster --project kenect-service-dev
kubectl port-forward kiali-pod -n istio-system 20002:20001
```

## Configuration System

### Environment Mapping
- UI environments: `dev`, `stage`, `prod`
- Maps to actual AWS profiles, GCP projects, database configs
- Abstraction handled by `EnvironmentMapper`

### Configuration Files
- `config/static/` - Template configurations
- `config/*.config` - Rendered environment-specific configs
- Environment variable support: `APEX_CONFIG_DIR`

This architecture enables APEX to serve as a unified command center for cloud operations while maintaining clean separation of concerns, real-time feedback, and environment abstraction.

## 📚 Documentation Architecture & Discovery Patterns

### Documentation Structure Layout

**Complete documentation is organized in `docs/` with logical subdirectories:**

```
docs/
├── architecture/           # System design and patterns
│   ├── discovery/          # Auto-discovery mechanisms
│   ├── providers/          # Provider integration patterns
│   ├── controllers/        # Controller orchestration
│   ├── routes/            # HTTP endpoint organization
│   └── ui/                # Frontend architecture
├── testing/               # Testing strategies and tools
│   ├── admin-capabilities/ # Admin Test Page documentation
│   ├── shadow/            # Shadow testing framework
│   └── validation/        # Multi-layer validation
├── operations/            # Operational procedures
│   ├── licensing/         # License management with examples
│   ├── deployment/        # Build and deployment guides
│   └── configuration/     # Config management patterns
└── infrastructure/        # Core infrastructure
    ├── lifecycle/         # Documentation lifecycle management
    └── patterns/          # Architectural patterns
```

### How to Consume Documentation

**📖 Reading Order for New Developers:**
1. **Start Here**: `WARP.md` (this file) - Overview and development commands
2. **Architecture**: `docs/README.md` - Complete system understanding
3. **Discovery Patterns**: `docs/architecture/discovery/` - Auto-loading mechanisms
4. **Testing**: `docs/testing/admin-capabilities/` - Admin Test Page usage
5. **Operations**: `docs/operations/licensing/` - License handling examples

**🔄 Documentation Lifecycle Process:**
- All docs follow versioned lifecycle in `docs/infrastructure/lifecycle/`
- Use llm-collector for codebase understanding: `python3 llm-collector/run.py`
- Documentation updates trigger via code changes and architecture evolution

## Auto-Discovery & Dynamic Loading Patterns

### Provider & Controller Auto-Discovery

**Registry Pattern Implementation:**

APEX uses sophisticated registry patterns for automatic discovery and loading of providers and controllers. Based on the codebase analysis, here's how auto-discovery works:

#### Controller Registry Auto-Discovery

```python
# web/controllers/__init__.py - ControllerRegistry class
class ControllerRegistry:
    def _init_controllers(self):
        """Auto-initialize all available controllers"""
        self._controllers = {
            "aws": AWSController(),      # Auto-discovered AWS controller
            "gcp": GCPController(),      # Auto-discovered GCP controller
            "k8s": K8sController(),      # Auto-discovered K8s controller
            "license": LicenseController() # Auto-discovered License controller
        }
        
    def register_controller(self, name: str, controller: BaseController):
        """Dynamic controller registration at runtime"""
        if self._provider_registry:
            controller.set_provider_registry(self._provider_registry)
        self._controllers[name] = controller
```

**Auto-Discovery Features:**
- **Automatic Registration**: Controllers auto-register on startup
- **Dynamic Loading**: New controllers can be registered at runtime
- **Dependency Injection**: Registry automatically wires dependencies
- **Status Aggregation**: Global status from all controllers

#### Provider Registry Auto-Discovery

```python
# web/providers/__init__.py - ProviderRegistry class  
class ProviderRegistry:
    def register_provider(self, name: str, provider: BaseProvider):
        """Auto-wire providers with WebSocket broadcasting"""
        if self._websocket_manager:
            provider.broadcast_message = self._websocket_manager.broadcast_message
        self._providers[name] = provider

# Auto-registered providers in web/main.py
aws_auth = AWSAuth()            # AWS authentication provider
gcp_auth = GCPAuth()            # GCP authentication provider  
gcp_k8s = GCPK8s()              # GCP Kubernetes provider
k8s_operations = K8sOperations()  # Kubernetes operations provider
license_provider = LicenseProvider() # License management provider
```

#### Route Auto-Discovery

**Organized Route Discovery Pattern:**

```python
# web/routes/__init__.py - Auto-discovery of all route modules
def setup_all_routes(app, controller_registry):
    """Auto-setup all routes organized by provider"""
    setup_core_routes(app, controller_registry)     # Core system routes
    setup_aws_routes(app, controller_registry)      # AWS provider routes
    setup_gcp_routes(app, controller_registry)      # GCP provider routes
    setup_k8s_routes(app, controller_registry)      # K8s provider routes
```

**Route Organization Pattern:**
- `/api/aws/*` - Auto-discovered AWS routes
- `/api/gcp/*` - Auto-discovered GCP routes  
- `/api/k8s/*` - Auto-discovered K8s routes
- `/api/{status,config,auth}` - Core system routes

### All Endpoints Discovery API

**Dynamic Endpoint Enumeration:**

```python
# Auto-generated from FastAPI route discovery
def list_all_routes(app):
    """Discover all registered routes dynamically"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': getattr(route, 'name', 'unnamed')
            })
    return routes
```

**Available via**: `GET /api/endpoints/all` (auto-generated from route discovery)

### Configuration Auto-Discovery

**Environment-Agnostic Config Loading:**

```python
# Auto-discovery of configuration files
config_files = {
    'aws.sso.config': 'AWS SSO profiles and authentication',
    'aws.db.config': 'Database connection configurations', 
    'static/gcp.config': 'GCP projects and cluster mappings',
    'static/gh.config': 'GitHub repository configurations'
}

# Auto-mapping of UI environments to actual resources
def get_aws_profile_for_env(env):
    """Auto-discover actual AWS profile from UI environment"""
    return config_mapping[env]['aws_profile']  # dev → actual profile
    
def get_gcp_project_for_env(env): 
    """Auto-discover actual GCP project from UI environment"""
    return config_mapping[env]['gcp_project']  # dev → kenect-service-dev
```

## Admin Test Capabilities Documentation

### Admin Test Page Overview

**Location**: `http://localhost:8000/static/admin.html`

The Admin Test Capabilities page provides comprehensive testing interface for all providers and system capabilities. Based on codebase analysis:

#### Page Structure & Navigation

**Cyberpunk-themed Admin Interface with organized sections:**

```javascript
// Navigation structure from admin.html
navItems = {
    // Provider Testing Sections
    awsProvider: 'AWS Provider Authentication & Capabilities',
    gcpProvider: 'GCP Provider Authentication & Capabilities', 
    k8sProvider: 'Kubernetes Provider Operations',
    
    // Command Testing Sections  
    awsCommands: 'Direct AWS CLI Command Execution',
    gcpCommands: 'Direct GCP CLI Command Execution',
    kubectlCommands: 'Direct kubectl Command Execution',
    
    // System Information
    systemStatus: 'Live System Status & Metrics',
    apiTesting: 'API Endpoint Testing',
    logsViewer: 'Real-time Log Streaming'
}
```

#### AWS Provider Test Capabilities

**Authentication Testing Across Environments:**

```html
<!-- Auto-generated status cards for each environment -->
<div class="status-card" onclick="testAWSAuth('dev')">
    <div class="status-icon">🟢</div>
    <div class="status-label">DEV Environment (WARP-FAKE-ACCOUNT-232143722969)</div>
    <div class="status-value">Click to Test WARP Demo Auth</div>
</div>
```

**Capability Testing Buttons:**
- **Identity Test**: `aws sts get-caller-identity` - Validates current authentication
- **Profile List**: Enumerate available AWS profiles
- **Region List**: Test region discovery and access
- **Profile Switching**: Dynamic profile switching validation

**Quick Command Testing:**
```javascript
// Pre-configured WARP test commands with fake data
quickCommands = {
    identity: 'aws sts get-caller-identity',
    ec2: 'aws ec2 describe-instances --max-items 5',  
    s3: 'aws s3 ls',  // Shows WARP-demo-bucket-test
    rds: 'aws rds describe-db-instances', // Shows WARP-test-db
    iam: 'aws iam get-user',  // Shows WARP-test-user
    route53: 'aws route53 list-hosted-zones'  // Shows WARP-demo.com zone
}
```

#### GCP Provider Test Capabilities

**Project Authentication Testing:**

```html
<div class="status-card" onclick="testGCPAuth('dev')">
    <div class="status-icon">🟢</div> 
    <div class="status-label">DEV Project (WARP-demo-service-dev)</div>
    <div class="status-value">Click to Test WARP Demo Project</div>
</div>
```

**GCP Capabilities:**
- **Auth List**: `gcloud auth list` - Shows WARP-test@example.com
- **Project List**: `gcloud projects list` - Shows WARP demo projects
- **Switch Project**: Dynamic project context switching
- **Config Test**: Validate gcloud configuration

**Quick GCP Commands:**
```javascript
gcpQuickCommands = {
    authList: 'gcloud auth list',  // Shows WARP-test@warp-demo.com
    projects: 'gcloud projects list',  // Shows WARP-demo-project-*
    vms: 'gcloud compute instances list --limit=5',  // Shows WARP-test-vm
    buckets: 'gcloud storage buckets list',  // Shows WARP-demo-bucket
    gke: 'gcloud container clusters list',  // Shows WARP-demo-cluster
    sql: 'gcloud sql instances list'  // Shows WARP-test-db
}
```

#### Kubernetes Provider Test Capabilities

**Cluster Connectivity Testing:**

```javascript
k8sCapabilities = {
    clusterInfo: 'kubectl cluster-info',     // Shows WARP demo cluster
    contexts: 'kubectl config get-contexts', // Shows WARP-demo-context
    namespaces: 'kubectl get namespaces',    // Shows WARP-test namespace
    nodes: 'kubectl get nodes',              // Shows WARP-demo-node
    pods: 'kubectl get pods --all-namespaces', // Shows WARP test pods
    services: 'kubectl get services'         // Shows WARP demo services
}
```

#### Real-Time Testing & Validation

**Multi-Layer Testing Implementation:**

```javascript
// Admin page implements multi-layer validation as per WARP rules
class AdminTestValidator {
    async executeTest(provider, capability) {
        // Layer 1: Direct API call
        const apiResult = await this.callProviderAPI(provider, capability);
        
        // Layer 2: Command verification  
        const cmdResult = await this.executeCommand(provider, capability);
        
        // Layer 3: Real-time WebSocket validation
        const wsResult = await this.validateViaWebSocket(provider, capability);
        
        // Layer 4: Background validation with tmp logging
        const bgResult = await this.backgroundValidation(provider, capability);
        
        return this.aggregateResults([apiResult, cmdResult, wsResult, bgResult]);
    }
}
```

**Background Testing with Tmp Logging:**
```javascript
// As per WARP rules - use backgrounding and tmp logging for risky tests
async function backgroundTestWithLogging(testFunction, testName) {
    const logFile = `/tmp/warp-admin-test-${Date.now()}.log`;
    
    try {
        // Execute test in background with timeout
        const result = await Promise.race([
            testFunction(),
            new Promise((_, reject) => setTimeout(() => reject('timeout'), 30000))
        ]);
        
        // Log success
        await logToFile(logFile, `✅ ${testName} completed successfully`);
        return result;
        
    } catch (error) {
        // Log failure for debugging
        await logToFile(logFile, `❌ ${testName} failed: ${error}`);
        throw error;
    }
}
```

### Admin Page Testing Automation

**Shadow Testing Integration:**

From `web/testing/shadow/utils/admin-page.js`, the Admin page supports full automation:

```javascript
// Complete admin page automation for testing
class AdminPage {
    // Auto-discovery of available profiles
    async loadAvailableProfiles() {
        const response = await this.page.evaluate(async () => {
            const resp = await fetch('/api/config/profiles');
            return await resp.json();
        });
        
        return {
            aws: response.aws_profiles,      // Auto-discovered AWS profiles
            gcp: response.gcp_projects,      // Auto-discovered GCP projects  
            aws_details: response.aws_profile_details,
            gcp_details: response.gcp_project_details
        };
    }
    
    // Automated capability testing
    async testAWSCapability(capability) {
        await this.navigateToSection('awsProvider');
        await this.page.click(this.aws.capabilities[capability]);
        await this.waitForResults();
        return this.extractTestResults();
    }
}
```

## Licensing Management & Fake Examples

### License System Architecture

**Provider-Based License Management:**

Based on `web/providers/license.py`, the license system uses:

```python
class LicenseProvider(BaseProvider):
    """Handles license operations with keychain integration"""
    
    def __init__(self):
        super().__init__("license")
        # WARP FAKE DEMO key for testing - not for production
        self._demo_key = "WARP_demo_license_key_32_chars_!"
        self._keychain_service = "apex-license"
        self._keychain_account = "APEX"
```

### Fake License Examples for Testing

**Demo User Accounts & License Keys:**

```python
# WARP FAKE license examples for testing and demos
WARP_DEMO_LICENSES = {
    "trial_user": {
        "email": "warp-demo-user@warp-test.com",
        "name": "WARP Demo User", 
        "license_key": "WARP-DEMO-TRIAL-1234-5678-9ABC-DEF0",
        "type": "trial",
        "days_remaining": 7,
        "features": ["basic", "warp_demo"]
    },
    "enterprise_user": {
        "email": "warp-enterprise@warp-test.com",
        "name": "WARP Enterprise Demo",
        "license_key": "WARP-ENT-DEMO-ABCD-EFGH-IJKL-MNOP", 
        "type": "enterprise",
        "days_remaining": 365,
        "features": ["basic", "enterprise", "admin_panel", "warp_demo"]
    },
    "expired_user": {
        "email": "warp-expired@warp-test.com",
        "name": "WARP Expired Demo",
        "license_key": "WARP-EXP-DEMO-9999-8888-7777-6666",
        "type": "expired", 
        "days_remaining": -5,
        "features": []
    }
}
```

**License Generation for Testing:**

```python
# WARP FAKE license generation - adds WARP watermarks
async def generate_trial_license(self, user_email: str, days: int = 7):
    """Generate WARP DEMO trial license"""
    # Add WARP demo watermarking as per rules
    license_data = {
        "user_email": f"WARP-DEMO-{user_email}",
        "user_name": f"WARP Test {user_email.split('@')[0].title()}",
        "expires": expires_date.isoformat(),
        "features": ["basic", "warp_demo_trial"],  # WARP watermark
        "license_type": "WARP_DEMO_TRIAL",  # WARP watermark
        "generated_at": datetime.now().isoformat(),
        "watermark": "WARP_FAKE_DEMO_LICENSE"  # Clear watermark
    }
```

**License Validation Examples:**

```python
# Example license status responses with WARP watermarks
LICENSE_STATUS_EXAMPLES = {
    "active_demo": {
        "success": True,
        "status": "active", 
        "message": "WARP Demo License Active",
        "user_email": "warp-demo@warp-test.com",
        "user_name": "WARP Demo User",
        "expires": "2025-01-01T00:00:00Z",
        "features": ["basic", "warp_demo"],
        "license_type": "WARP_DEMO",
        "days_remaining": 30
    },
    "invalid_demo": {
        "success": True,
        "status": "invalid",
        "message": "WARP Demo License Invalid - Test Scenario",
        "user_email": None,
        "features": [],
        "license_type": None,
        "days_remaining": None
    }
}
```

**License Error Handling Examples:**

```python
# WARP FAKE error scenarios for testing
LICENSE_ERROR_EXAMPLES = {
    "network_error": "WARP Demo: License server unavailable (fake error)",
    "invalid_key": "WARP Demo: Invalid license key format (test scenario)",
    "expired": "WARP Demo: License expired on WARP-fake-date (test)",
    "user_mismatch": "WARP Demo: License assigned to different WARP test user"
}
```

### License UI Integration

**License Modal with Fake Data:**

From `web/templates/components/licensing/license_modal.html`:

```html
<!-- WARP Demo License Modal -->
<div class="license-demo-section">
    <h3>WARP Demo License Examples</h3>
    <div class="demo-license-cards">
        <div class="license-card">
            <h4>Trial License (WARP Demo)</h4>
            <code>WARP-DEMO-TRIAL-1234-5678-9ABC-DEF0</code>
            <p>Email: warp-demo@warp-test.com</p>
            <p>Status: Active (WARP Demo)</p>
        </div>
        
        <div class="license-card">
            <h4>Enterprise License (WARP Demo)</h4> 
            <code>WARP-ENT-DEMO-ABCD-EFGH-IJKL-MNOP</code>
            <p>Email: warp-enterprise@warp-test.com</p>
            <p>Status: Active (WARP Demo)</p>
        </div>
    </div>
</div>
```

## Documentation Lifecycle Management

### Core Infrastructure Documentation Process

**Integrated Lifecycle Management:**

Documentation lifecycle is managed through:

1. **Code-Driven Updates**: Documentation automatically updated when code changes
2. **LLM-Collector Integration**: Use `python3 llm-collector/run.py` for full codebase analysis
3. **Architecture Evolution Tracking**: Document changes as architecture evolves
4. **Version-Controlled Documentation**: All docs in git with proper versioning

### Documentation Update Triggers

**Automatic Documentation Updates:**

```python
# Documentation lifecycle triggers
DOCUMENTATION_TRIGGERS = {
    "provider_added": "Update provider discovery docs",
    "controller_added": "Update controller registry docs", 
    "route_added": "Update endpoint documentation",
    "config_changed": "Update configuration examples",
    "feature_added": "Update capability documentation"
}
```

**LLM-Collector Integration:**

```bash
# Always start with full codebase understanding
python3 llm-collector/run.py  # Generates complete codebase flat file

# Use results for documentation updates
cat llm-collector/results.json | jq '.providers' # Analyze provider changes
cat llm-collector/results.json | jq '.controllers' # Analyze controller changes  
cat llm-collector/results.json | jq '.routes' # Analyze route changes
```

### Documentation Coherence Rules

**Maintaining Documentation Coherence:**

1. **Single Source of Truth**: WARP.md is the primary developer reference
2. **Logical Organization**: docs/ contains detailed specialized documentation
3. **Auto-Discovery First**: Document how things are discovered, not just what they are
4. **Fake Data Watermarking**: All examples clearly marked with WARP/FAKE/DEMO labels
5. **Multi-Layer Validation**: Document testing at all levels (unit, integration, e2e)

**Documentation Dependencies:**

```
WARP.md (Primary)
├── docs/README.md (Secondary overview)
├── docs/architecture/discovery/ (Auto-discovery details)
├── docs/testing/admin-capabilities/ (Admin page details)  
├── docs/operations/licensing/ (License examples)
└── docs/infrastructure/lifecycle/ (Process documentation)
```

**Quality Gates:**

- Every new provider/controller must update auto-discovery docs
- Every new capability must be added to Admin Test page documentation
- All examples must include WARP watermarks for clarity
- Documentation must be validated with multi-layer testing approach
- Updates trigger via code changes and LLM-collector analysis
