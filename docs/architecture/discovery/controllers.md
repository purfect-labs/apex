# Controller Registry Lifecycle & Dependency Injection Documentation

## 🎯 Controller Registry Architecture

The APEX Controller Registry implements centralized controller lifecycle management with automatic dependency injection of provider registries and WebSocket managers. This enables coordinated business logic execution across all cloud services.

## 📁 Controller Registry Implementation

**Registry Location**: `web/controllers/__init__.py`  
**Base Controller**: `web/controllers/base_controller.py`  
**Initialization**: Lines 22-36 (`_init_controllers` method)

### ControllerRegistry Class Structure

```python
# File: web/controllers/__init__.py
class ControllerRegistry:
    """Registry for managing all controllers with lifecycle management"""
    
    def __init__(self):
        self._controllers: Dict[str, BaseController] = {}
        self._provider_registry = None
        self._websocket_manager = None
        
        # Initialize default controllers automatically
        self._init_controllers()
    
    def _init_controllers(self):
        """Initialize all available controllers with auto-discovery"""
        # AWS Controller
        self._controllers["aws"] = AWSController()
        
        # GCP Controller  
        self._controllers["gcp"] = GCPController()
        
        # K8s Controller
        self._controllers["k8s"] = K8sController()
        
        # License Controller
        self._controllers["license"] = LicenseController()
    
    def register_controller(self, name: str, controller: BaseController):
        """Register a custom controller with dependency injection"""
        if self._provider_registry:
            controller.set_provider_registry(self._provider_registry)
        if self._websocket_manager:
            controller.set_websocket_manager(self._websocket_manager)
        
        self._controllers[name] = controller
    
    def unregister_controller(self, name: str):
        """Unregister a controller"""
        if name in self._controllers:
            del self._controllers[name]
```

### Dependency Injection System

```python
# Auto-wire provider registry to all controllers
def set_provider_registry(self, provider_registry):
    """Set the provider registry for all controllers"""
    self._provider_registry = provider_registry
    for controller in self._controllers.values():
        controller.set_provider_registry(provider_registry)

# Auto-wire WebSocket manager to all controllers
def set_websocket_manager(self, websocket_manager):
    """Set the WebSocket manager for all controllers"""
    self._websocket_manager = websocket_manager
    for controller in self._controllers.values():
        controller.set_websocket_manager(websocket_manager)
```

## 🚀 Controller Lifecycle Management

### 1. Controller Initialization Process

Based on the actual implementation from `web/controllers/__init__.py`:

```python
# File: web/controllers/__init__.py - Lines 24-36
def _init_controllers(self):
    """Initialize all available controllers"""
    # WARP-Demo: Actual controller initialization
    self._controllers["aws"] = AWSController()        # AWS business logic
    self._controllers["gcp"] = GCPController()        # GCP business logic
    self._controllers["k8s"] = K8sController()        # Kubernetes business logic
    self._controllers["license"] = LicenseController() # License management
```

### 2. Dependency Injection Flow

```python
# File: web/main.py - Lines 88-90 (Controller wiring in main app)
def _setup_architecture(self):
    """Wire up controller registry with dependencies"""
    # Step 1: Wire controller registry with provider registry
    self.controller_registry.set_provider_registry(self.provider_registry)
    
    # Step 2: Wire controller registry with WebSocket manager
    self.controller_registry.set_websocket_manager(self)
```

### 3. Controller Status Aggregation

```python
# File: web/controllers/__init__.py - Lines 117-134
async def get_global_status(self) -> Dict[str, Any]:
    """Get status from all controllers with aggregation"""
    status = {
        "controllers": {},
        "registry_info": {
            "total_controllers": len(self._controllers),
            "available_controllers": list(self._controllers.keys())  # ["aws", "gcp", "k8s", "license"]
        }
    }
    
    # WARP-Demo: Aggregate status from all controllers
    for name, controller in self._controllers.items():
        try:
            controller_status = await controller.get_status()
            status["controllers"][name] = controller_status
        except Exception as e:
            status["controllers"][name] = {"error": f"WARP-Demo: {str(e)}"}
    
    return status
```

## 📋 Currently Registered Controllers

Based on the actual codebase implementation:

### AWS Controller (`aws`)
- **Class**: `AWSController` from `web/controllers/aws_controller.py`
- **Purpose**: AWS CLI operations and profile management business logic
- **Registry Name**: `"aws"`
- **Dependencies**: `aws_auth` provider from ProviderRegistry

### GCP Controller (`gcp`)
- **Class**: `GCPController` from `web/controllers/gcp_controller.py`
- **Purpose**: GCP CLI operations and project management business logic
- **Registry Name**: `"gcp"`
- **Dependencies**: `gcp_auth`, `gcp_k8s` providers from ProviderRegistry

### Kubernetes Controller (`k8s`)
- **Class**: `K8sController` from `web/controllers/k8s_controller.py`
- **Purpose**: Kubernetes cluster operations and pod management business logic
- **Registry Name**: `"k8s"`
- **Dependencies**: `k8s_operations`, `gcp_k8s` providers from ProviderRegistry

### License Controller (`license`)
- **Class**: `LicenseController` from `web/controllers/license_controller.py`
- **Purpose**: License validation and keychain management business logic
- **Registry Name**: `"license"`
- **Dependencies**: `license` provider from ProviderRegistry

## 🔄 Controller Access Patterns

### Direct Controller Access

```python
# File: web/controllers/__init__.py - Lines 54-68
def get_aws_controller(self) -> AWSController:
    """Get the AWS controller"""
    return self._controllers.get("aws")

def get_gcp_controller(self) -> GCPController:
    """Get the GCP controller"""
    return self._controllers.get("gcp")

def get_k8s_controller(self) -> K8sController:
    """Get the K8s controller"""
    return self._controllers.get("k8s")

def get_license_controller(self) -> LicenseController:
    """Get the License controller"""
    return self._controllers.get("license")
```

### Global Registry Instance Pattern

```python
# File: web/controllers/__init__.py - Lines 137-171
# Singleton pattern for global controller access
controller_registry = ControllerRegistry()

def get_controller_registry() -> ControllerRegistry:
    """Get the global controller registry instance"""
    return controller_registry

# Convenience functions for direct access
def get_aws_controller() -> AWSController:
    """Get the AWS controller"""
    return controller_registry.get_aws_controller()

def get_gcp_controller() -> GCPController:
    """Get the GCP controller"""
    return controller_registry.get_gcp_controller()
```

## 🏗️ Base Controller Architecture

### BaseController Class Pattern

```python
# File: web/controllers/base_controller.py - Lines 11-71
class BaseController(ABC):
    """Base class for all APEX controllers with common functionality"""
    
    def __init__(self, name: str):
        self.name = name
        self.providers = {}
        self.broadcast_callback = None
    
    def set_provider_registry(self, provider_registry):
        """Set provider registry for accessing providers"""
        self.provider_registry = provider_registry
    
    def set_websocket_manager(self, websocket_manager):
        """Set WebSocket manager for broadcasting"""
        self.websocket_manager = websocket_manager
        self.set_broadcast_callback(websocket_manager.broadcast_message)
    
    def get_provider(self, provider_name: str):
        """Get a provider from the registry or local providers"""
        if hasattr(self, 'provider_registry') and self.provider_registry:
            return self.provider_registry.get_provider(provider_name)
        return self.providers.get(provider_name)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if self.broadcast_callback:
            await self.broadcast_callback(message)
    
    async def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log an action with optional details"""
        message = {
            'type': 'action_log',
            'data': {
                'controller': self.name,
                'action': action,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            }
        }
        await self.broadcast_message(message)
```

## 🔧 Dynamic Controller Registration

### Adding New Controller to Registry

```python
# WARP-Demo: Adding a new controller (e.g., Docker controller)
# File: web/controllers/__init__.py - register_controller method

# 1. Create controller class
from .docker_controller import DockerController

# 2. Register controller dynamically
def add_docker_controller():
    """WARP-Demo: Add Docker controller to registry"""
    docker_controller = DockerController()
    controller_registry.register_controller("docker", docker_controller)
    
    # Dependencies are auto-injected
    # - provider_registry is automatically wired
    # - websocket_manager is automatically wired

# 3. Access the new controller
docker_controller = controller_registry.get_controller("docker")
```

### Controller Registration Usage Pattern

```python
# WARP-Demo: How routes access controllers via registry
class APIRoutes:
    def __init__(self, controller_registry: ControllerRegistry):
        self.controller_registry = controller_registry
    
    async def aws_authenticate(self, profile: str):
        """AWS authentication via controller registry"""
        # Step 1: Get controller from registry
        aws_controller = self.controller_registry.get_aws_controller()
        
        if not aws_controller:
            return {"success": False, "error": "WARP-Demo: AWS controller not available"}
        
        # Step 2: Controller has auto-injected dependencies
        # - provider_registry (access to aws_auth provider)
        # - websocket_manager (real-time broadcasting)
        
        # Step 3: Execute business logic with real-time updates
        result = await aws_controller.authenticate_profile(profile)
        
        return {
            "success": result["success"],
            "message": f"WARP-Demo: Authentication via {aws_controller.name}",
            "profile": profile
        }
```

## 🌐 WebSocket Broadcasting Integration

### Automatic Broadcasting Setup

Every registered controller automatically receives WebSocket broadcasting capability:

```python
# File: web/controllers/__init__.py - Lines 44-48
def set_websocket_manager(self, websocket_manager):
    """Auto-wire WebSocket manager to all controllers"""
    self._websocket_manager = websocket_manager
    
    # CRITICAL: Wire all existing controllers
    for controller in self._controllers.values():
        controller.set_websocket_manager(websocket_manager)
```

### Controller Broadcasting Pattern

```python
# WARP-Demo: How controllers use auto-wired WebSocket broadcasting
class AWSController(BaseController):
    def __init__(self):
        super().__init__("aws_controller")
    
    async def authenticate_profile(self, profile: str):
        """Authenticate AWS profile with real-time updates"""
        # Use auto-wired broadcasting capability
        await self.log_action("authentication_started", {
            "profile": profile,
            "demo_marker": "WARP-Demo-AWS-Auth"
        })
        
        # Get provider via auto-injected provider registry
        aws_auth = self.get_provider("aws_auth")
        
        if not aws_auth:
            await self.handle_error("WARP-Demo: AWS provider not available")
            return {"success": False}
        
        # Execute with provider
        result = await aws_auth.authenticate(profile=profile)
        
        # Broadcast completion via auto-wired WebSocket
        await self.log_action("authentication_completed", {
            "profile": profile,
            "success": result["success"],
            "demo_marker": "WARP-Demo-Completed"
        })
        
        return result
```

## 🔍 Controller Status Discovery

### Global Status Aggregation

```python
# Get all controller statuses via registry
async def get_all_controller_status():
    """WARP-Demo: Discover and check all controller statuses"""
    controller_registry = get_controller_registry()
    global_status = await controller_registry.get_global_status()
    
    return {
        "registry_info": global_status["registry_info"],
        "controllers": {
            name: {
                "status": status,
                "class": controller_registry.get_controller(name).__class__.__name__,
                "provider_wired": hasattr(controller_registry.get_controller(name), 'provider_registry'),
                "websocket_wired": hasattr(controller_registry.get_controller(name), 'websocket_manager'),
                "demo_marker": f"WARP-Demo-{name.upper()}-Controller"
            } 
            for name, status in global_status["controllers"].items()
        },
        "demo_system": "WARP-Controller-Registry"
    }
```

### Controller Lifecycle Management

```python
# File: web/controllers/__init__.py - Lines 75-94
async def initialize_all(self):
    """Initialize all controllers with error handling"""
    for name, controller in self._controllers.items():
        try:
            if hasattr(controller, 'initialize'):
                await controller.initialize()
            print(f"✅ WARP-Demo: Initialized {name} controller")
        except Exception as e:
            print(f"❌ WARP-Demo: Failed to initialize {name} controller: {e}")

async def shutdown_all(self):
    """Shutdown all controllers gracefully"""
    for name, controller in self._controllers.items():
        try:
            if hasattr(controller, 'shutdown'):
                await controller.shutdown()
            print(f"✅ WARP-Demo: Shutdown {name} controller")
        except Exception as e:
            print(f"❌ WARP-Demo: Failed to shutdown {name} controller: {e}")
```

## 🚨 Controller Registry Error Handling

### Broadcasting Error Handling

```python
# File: web/controllers/__init__.py - Lines 109-115
async def broadcast_to_all(self, message: Dict[str, Any]):
    """Broadcast a message to all controllers with error handling"""
    for controller in self._controllers.values():
        try:
            await controller.broadcast_message(message)
        except Exception as e:
            print(f"WARP-Demo: Failed to broadcast to {controller.name}: {e}")
```

### Base Controller Error Handling

```python
# File: web/controllers/base_controller.py - Lines 45-56
async def handle_error(self, error: str, context: str = ""):
    """Handle and broadcast errors with WARP watermarking"""
    message = {
        'type': 'error',
        'data': {
            'controller': self.name,
            'error': f"WARP-Demo: {error}",  # WARP watermark
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
    }
    await self.broadcast_message(message)
```

## 📊 Controller Registry Architecture Benefits

✅ **Centralized Management**: Single registry manages all controller instances  
✅ **Automatic Dependency Injection**: Provider registries and WebSocket managers auto-wired  
✅ **Lifecycle Management**: Initialize/shutdown all controllers together  
✅ **Status Aggregation**: Global status from all controllers via single interface  
✅ **Dynamic Registration**: New controllers can be added at runtime  
✅ **Error Handling**: Centralized error broadcasting and handling  
✅ **Type Safety**: Strongly typed controller access methods  

## 🧪 Testing Controller Registry

### Registry Functionality Tests

```bash
# WARP-Demo: Test controller registry functionality
curl http://localhost:8000/api/status

# Expected response showing all controllers:
{
  "controllers": {
    "aws": {"status": "ready", "demo": "WARP-AWS"},
    "gcp": {"status": "ready", "demo": "WARP-GCP"},
    "k8s": {"status": "ready", "demo": "WARP-K8S"},
    "license": {"status": "ready", "demo": "WARP-LICENSE"}
  },
  "registry_info": {
    "total_controllers": 4,
    "available_controllers": ["aws", "gcp", "k8s", "license"]
  }
}
```

### Dependency Injection Tests

```python
# WARP-Demo: Test controller dependency injection
async def test_controller_dependency_injection():
    controller_registry = get_controller_registry()
    
    # Test each controller has required dependencies
    for name in ["aws", "gcp", "k8s", "license"]:
        controller = controller_registry.get_controller(name)
        
        assert hasattr(controller, 'provider_registry'), f"WARP-Demo: {name} missing provider_registry"
        assert hasattr(controller, 'websocket_manager'), f"WARP-Demo: {name} missing websocket_manager"
        
        # Test provider access works
        if name == "aws":
            aws_provider = controller.get_provider("aws_auth")
            assert aws_provider is not None, "WARP-Demo: AWS controller can't access aws_auth provider"
```

---

## 📝 Controller Registry Documentation Maintenance

**⚠️ CRITICAL: When controller architecture changes, update this documentation immediately:**

### New Controller Added
- [ ] Add controller class to `_init_controllers()` method in `web/controllers/__init__.py`
- [ ] Update "Currently Registered Controllers" section with new controller details
- [ ] Add controller access method (`get_xxx_controller`)
- [ ] Add controller to testing examples
- [ ] Verify dependency injection works for new controller

### Controller Registration Changed
- [ ] Update `_init_controllers()` method examples
- [ ] Update controller initialization pattern examples
- [ ] Update dependency injection flow documentation
- [ ] Test all controller discovery functionality still works

### Dependency Injection Changed
- [ ] Update `set_provider_registry()` and `set_websocket_manager()` examples
- [ ] Update auto-wiring mechanism documentation
- [ ] Update BaseController integration examples
- [ ] Test provider access and WebSocket broadcasting works

### Controller Base Class Modified
- [ ] Update BaseController examples
- [ ] Update broadcasting and logging patterns
- [ ] Update provider access methods
- [ ] Verify all controllers still inherit correctly

### Testing Controller Changes

```bash
# Test controller registry and dependency injection
cd /Users/warp-demo-user/code/github/apex
python3 -m pytest tests/ -k "test_controller" -v

# Test registry functionality
python3 web/main.py &
curl http://localhost:8000/api/status
curl http://localhost:8000/api/aws/status
curl http://localhost:8000/api/gcp/status

# Verify dependency injection works
# (Test each controller can access its required providers)
```

**Documentation Dependencies:**
- **Primary**: `docs/architecture/discovery/controllers.md` (this file)
- **Secondary**: `docs/architecture/discovery/providers.md` (provider registry)
- **Implementation**: `web/controllers/__init__.py`, `web/controllers/base_controller.py`
- **Related**: Controller-specific implementation files

This controller registry system enables APEX to coordinate business logic across all cloud services with centralized dependency injection and lifecycle management.