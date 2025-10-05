# Provider Auto-Discovery & Registry Pattern Documentation

## 🔌 Provider Registry Architecture

The APEX Provider Registry implements automatic discovery, registration, and dependency injection for all cloud service providers. This enables dynamic loading of providers with automatic WebSocket broadcasting capabilities.

## 📁 Provider Registry Implementation

**Registry Location**: `web/providers/__init__.py`  
**Entry Point**: `web/main.py` - Line 100-104 (provider registration)

### ProviderRegistry Class Structure

```python
# File: web/providers/__init__.py
class ProviderRegistry:
    """Registry for managing all providers with auto-discovery capabilities"""
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._websocket_manager = None
    
    def register_provider(self, name: str, provider: BaseProvider):
        """Register a provider with automatic WebSocket wiring"""
        if self._websocket_manager:
            provider.broadcast_message = self._websocket_manager.broadcast_message
        self._providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get a provider by registered name"""
        return self._providers.get(name)
    
    def set_websocket_manager(self, websocket_manager):
        """Auto-wire WebSocket manager to all registered providers"""
        self._websocket_manager = websocket_manager
        for provider in self._providers.values():
            provider.broadcast_message = websocket_manager.broadcast_message
    
    def list_providers(self) -> Dict[str, str]:
        """List all registered providers with class names"""
        return {name: provider.__class__.__name__ for name, provider in self._providers.items()}
```

### Global Registry Instance Pattern

```python
# File: web/providers/__init__.py
# Singleton pattern for global provider access
_provider_registry = ProviderRegistry()

def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry instance"""
    return _provider_registry
```

## 🚀 Provider Auto-Discovery Flow

### 1. Provider Registration Process (Main App Initialization)

```python
# File: web/main.py - Lines 93-104
def _setup_architecture(self):
    """Setup the three-tier architecture: Controllers -> Providers -> APIs"""
    # Wire up provider registry with WebSocket manager
    self.provider_registry.set_websocket_manager(self)
    
    # Initialize providers through auto-discovery pattern
    aws_auth = AWSAuth()                    # WARP-Demo: AWS Auth Provider
    gcp_auth = GCPAuth()                    # WARP-Demo: GCP Auth Provider  
    gcp_k8s = GCPK8s()                      # WARP-Demo: GCP K8s Provider
    k8s_operations = K8sOperations()        # WARP-Demo: K8s Operations Provider
    license_provider = LicenseProvider()    # WARP-Demo: License Provider
    
    # Register providers with auto-wiring to WebSocket broadcasting
    self.provider_registry.register_provider("aws_auth", aws_auth)
    self.provider_registry.register_provider("gcp_auth", gcp_auth) 
    self.provider_registry.register_provider("gcp_k8s", gcp_k8s)
    self.provider_registry.register_provider("k8s_operations", k8s_operations)
    self.provider_registry.register_provider("license", license_provider)
```

### 2. WebSocket Auto-Wiring Mechanism

```python
# When providers are registered, they automatically get WebSocket broadcasting
def register_provider(self, name: str, provider: BaseProvider):
    """Auto-wire providers with real-time broadcasting capability"""
    # CRITICAL: Auto-wire WebSocket broadcasting to provider
    if self._websocket_manager:
        provider.broadcast_message = self._websocket_manager.broadcast_message
    
    # Store in registry for controller access
    self._providers[name] = provider
```

### 3. Provider Discovery By Controllers

Controllers use the registry to discover available providers dynamically:

```python
# WARP-Demo: Controller accessing providers via registry
class AWSController(BaseController):
    def get_auth_provider(self) -> Optional[AWSAuth]:
        """Discover AWS auth provider via registry"""
        return self.provider_registry.get_provider("aws_auth")
    
    async def authenticate_profile(self, profile: str):
        # Auto-discover provider
        aws_auth = self.get_auth_provider()
        if not aws_auth:
            return {"success": False, "error": "WARP-Demo: AWS provider not discovered"}
        
        # Provider has auto-wired WebSocket broadcasting
        return await aws_auth.authenticate(profile=profile)
```

## 📋 Currently Registered Providers

Based on the actual codebase implementation:

### AWS Provider (`aws_auth`)
- **Class**: `AWSAuth` from `web/providers/aws/auth.py`
- **Purpose**: AWS CLI authentication and profile management
- **Auto-Discovery Name**: `"aws_auth"`
- **WebSocket Integration**: ✅ Auto-wired for real-time SSO flows

### GCP Provider (`gcp_auth`)
- **Class**: `GCPAuth` from `web/providers/gcp/auth.py`
- **Purpose**: GCP CLI authentication and project management
- **Auto-Discovery Name**: `"gcp_auth"`
- **WebSocket Integration**: ✅ Auto-wired for real-time auth flows

### GCP Kubernetes Provider (`gcp_k8s`)
- **Class**: `GCPK8s` from `web/providers/gcp/k8s.py`
- **Purpose**: kubectl operations through GCP clusters
- **Auto-Discovery Name**: `"gcp_k8s"`
- **WebSocket Integration**: ✅ Auto-wired for Kiali port forwarding

### Kubernetes Operations Provider (`k8s_operations`)
- **Class**: `K8sOperations` from `web/providers/k8s/operations.py`
- **Purpose**: Direct kubectl operations and cluster management
- **Auto-Discovery Name**: `"k8s_operations"`
- **WebSocket Integration**: ✅ Auto-wired for pod/service operations

### License Provider (`license`)
- **Class**: `LicenseProvider` from `web/providers/license.py`
- **Purpose**: License validation and keychain management
- **Auto-Discovery Name**: `"license"`
- **WebSocket Integration**: ✅ Auto-wired for license status broadcasts

## 🔄 Dynamic Provider Registration Examples

### Adding New Provider to Registry

```python
# WARP-Demo: Adding a new provider (e.g., Docker provider)
# File: web/main.py - _setup_architecture method

# 1. Import provider class
from .providers.docker.operations import DockerOperations

# 2. Initialize provider in architecture setup
def _setup_architecture(self):
    # ... existing providers ...
    
    # Initialize new WARP-Demo Docker provider
    docker_operations = DockerOperations()
    
    # Auto-register with WebSocket wiring
    self.provider_registry.register_provider("docker_operations", docker_operations)
```

### Provider Auto-Discovery Usage Pattern

```python
# WARP-Demo: How controllers discover and use providers
class DockerController(BaseController):
    async def list_containers(self, env: str = "dev"):
        """List Docker containers via auto-discovered provider"""
        # Step 1: Auto-discover provider via registry
        docker_provider = self.provider_registry.get_provider("docker_operations")
        
        if not docker_provider:
            return {
                "success": False, 
                "error": "WARP-Demo: Docker provider not available in registry"
            }
        
        # Step 2: Provider automatically has WebSocket broadcasting
        # (auto-wired during registration)
        
        # Step 3: Execute operation with real-time output
        result = await docker_provider.execute_command("docker ps --format table")
        
        return {
            "success": result["success"],
            "containers": self.parse_docker_output(result.get("stdout", "")),
            "provider": "WARP-Demo-Docker-Operations"  # WARP watermark
        }
```

## 🌐 WebSocket Broadcasting Auto-Wiring

### Automatic Broadcasting Setup

Every registered provider automatically receives WebSocket broadcasting capability:

```python
# When provider registry is wired with WebSocket manager
def set_websocket_manager(self, websocket_manager):
    """Auto-wire all providers with real-time broadcasting"""
    self._websocket_manager = websocket_manager
    
    # CRITICAL: Wire all existing providers
    for provider in self._providers.values():
        provider.broadcast_message = websocket_manager.broadcast_message
```

### Provider Base Class Integration

```python
# File: web/providers/base_provider.py
class BaseProvider(ABC):
    async def execute_command(self, command: str, env: Optional[Dict[str, str]] = None, stream_output: bool = True):
        """Execute command with auto-wired real-time streaming"""
        
        # Show command execution via auto-wired WebSocket
        if stream_output:
            await self.broadcast_message({
                'type': 'command_output',
                'data': {
                    'output': f'⚡ WARP-Demo: {command}',  # WARP watermark
                    'context': self.name
                }
            })
        
        # Real-time output streaming (auto-wired during registration)
        # ... command execution with live output broadcasting ...
```

## 🔍 Provider Status Discovery

### Dynamic Provider Status Aggregation

```python
# Get all provider statuses via registry
async def get_all_provider_status():
    """WARP-Demo: Discover and check all provider statuses"""
    provider_registry = get_provider_registry()
    statuses = {}
    
    for name, provider in provider_registry._providers.items():
        try:
            status = await provider.get_status()
            statuses[name] = {
                "class": provider.__class__.__name__,
                "status": status,
                "websocket_wired": hasattr(provider, 'broadcast_message'),
                "demo_marker": "WARP-Demo-Provider"  # WARP watermark
            }
        except Exception as e:
            statuses[name] = {
                "class": provider.__class__.__name__, 
                "error": f"WARP-Demo Error: {str(e)}",  # WARP watermark
                "websocket_wired": hasattr(provider, 'broadcast_message')
            }
    
    return statuses
```

### Provider Capability Discovery

```python
# File: web/main.py - Dynamic endpoint discovery
@self.app.get("/api/providers/list")
async def list_providers():
    """Auto-discover all registered providers"""
    provider_list = self.provider_registry.list_providers()
    
    return {
        "providers": provider_list,
        "count": len(provider_list),
        "auto_discovery": True,
        "websocket_integrated": True,
        "demo_system": "WARP-Provider-Registry"  # WARP watermark
    }
```

## 🚨 Provider Registry Error Handling

### Missing Provider Handling

```python
def get_provider(self, name: str) -> Optional[BaseProvider]:
    """Safe provider retrieval with error handling"""
    provider = self._providers.get(name)
    
    if not provider:
        # Log missing provider for debugging
        logging.warning(f"WARP-Demo: Provider '{name}' not found in registry")
        logging.info(f"Available providers: {list(self._providers.keys())}")
    
    return provider
```

### WebSocket Wiring Validation

```python
def validate_provider_websocket_wiring(self):
    """WARP-Demo: Validate all providers have WebSocket broadcasting"""
    unwired_providers = []
    
    for name, provider in self._providers.items():
        if not hasattr(provider, 'broadcast_message'):
            unwired_providers.append(name)
    
    if unwired_providers:
        logging.error(f"WARP-Demo: Providers missing WebSocket wiring: {unwired_providers}")
        return False
    
    return True
```

## 📊 Provider Registry Architecture Benefits

✅ **Automatic Discovery**: Controllers can find providers without hardcoding dependencies  
✅ **WebSocket Auto-Wiring**: All providers automatically get real-time broadcasting  
✅ **Dynamic Registration**: New providers can be added without modifying existing code  
✅ **Centralized Management**: Single registry manages all provider instances  
✅ **Dependency Injection**: Registry handles provider lifecycle and wiring  
✅ **Status Aggregation**: Can query all provider statuses through single interface  

## 🧪 Testing Provider Auto-Discovery

### Registry Functionality Tests

```bash
# WARP-Demo: Test provider registry functionality
curl http://localhost:8000/api/providers/list

# Expected response:
{
  "providers": {
    "aws_auth": "AWSAuth",
    "gcp_auth": "GCPAuth", 
    "gcp_k8s": "GCPK8s",
    "k8s_operations": "K8sOperations",
    "license": "LicenseProvider"
  },
  "count": 5,
  "auto_discovery": true,
  "websocket_integrated": true,
  "demo_system": "WARP-Provider-Registry"
}
```

### WebSocket Wiring Tests

```python
# WARP-Demo: Test provider WebSocket integration
async def test_provider_websocket_wiring():
    provider_registry = get_provider_registry()
    
    # Test each provider has broadcast capability
    for name, provider in provider_registry._providers.items():
        assert hasattr(provider, 'broadcast_message'), f"WARP-Demo: {name} missing WebSocket wiring"
        
        # Test broadcasting works
        await provider.broadcast_message({
            'type': 'test_message',
            'data': {'test': f'WARP-Demo broadcast from {name}'}
        })
```

---

## 📝 Provider Discovery Documentation Maintenance

**⚠️ CRITICAL: When provider architecture changes, update this documentation immediately:**

### New Provider Added
- [ ] Add provider class to registry registration in `web/main.py`
- [ ] Update "Currently Registered Providers" section with new provider details
- [ ] Add provider import to registry examples
- [ ] Add provider to testing examples
- [ ] Verify WebSocket auto-wiring works for new provider

### Provider Registration Changed
- [ ] Update `_setup_architecture()` method examples
- [ ] Update provider registration pattern examples  
- [ ] Update auto-discovery flow documentation
- [ ] Test all provider discovery functionality still works

### WebSocket Integration Changed
- [ ] Update `set_websocket_manager()` examples
- [ ] Update auto-wiring mechanism documentation
- [ ] Update provider broadcasting examples
- [ ] Test real-time output streaming works

### Provider Base Class Modified
- [ ] Update BaseProvider integration examples
- [ ] Update command execution patterns
- [ ] Update broadcasting message formats
- [ ] Verify all providers still inherit correctly

### Testing Provider Changes

```bash
# Test provider discovery and WebSocket integration
cd /Users/warp-demo-user/code/github/apex
python3 -m pytest tests/ -k "test_provider" -v

# Test registry functionality  
python3 web/main.py &
curl http://localhost:8000/api/providers/list
curl http://localhost:8000/api/status

# Verify WebSocket broadcasting works
# (Connect to WebSocket and trigger provider operations)
```

**Documentation Dependencies:**
- **Primary**: `docs/architecture/discovery/providers.md` (this file)
- **Secondary**: `docs/architecture/README.md` (architecture overview)
- **Implementation**: `web/providers/__init__.py`, `web/main.py`
- **Testing**: Provider-specific test files

This provider auto-discovery system enables APEX to dynamically manage cloud service integrations with automatic real-time communication capabilities.