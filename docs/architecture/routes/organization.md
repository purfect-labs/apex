# Route Organization & Dynamic Endpoint Discovery Documentation

## 🌐 Route Organization Architecture

The APEX Route system implements organized API endpoint discovery with provider-specific routing patterns and dynamic endpoint enumeration. This enables scalable REST API organization with automatic route registration and discovery.

## 📁 Route System Implementation

**Main Router**: `web/routes/__init__.py`  
**Setup Function**: `setup_all_routes(app, controller_registry)` - Lines 12-28  
**Discovery Function**: `list_all_routes(app)` - Lines 30-40

### setup_all_routes Pattern

```python
# File: web/routes/__init__.py - Lines 12-28
def setup_all_routes(app, controller_registry):
    """Setup all routes organized by provider"""
    
    # Core system routes (status, config, etc)
    setup_core_routes(app, controller_registry)
    
    # Provider-specific routes
    setup_aws_routes(app, controller_registry)
    setup_gcp_routes(app, controller_registry)
    setup_k8s_routes(app, controller_registry)
    
    print("📡 All routes organized by provider and capability")
    print("   - AWS: /api/aws/*")
    print("   - GCP: /api/gcp/*") 
    print("   - K8s: /api/k8s/*")
    print("   - Core: /api/{status,config,auth}")
```

### Dynamic Endpoint Enumeration

```python
# File: web/routes/__init__.py - Lines 30-40
def list_all_routes(app):
    """List all registered routes for debugging"""
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

## 🚀 Route Module Organization

### 1. Core Routes (`/api/config/*`, `/api/status`)

**Module Location**: `web/routes/core/__init__.py`

```python
# File: web/routes/core/__init__.py
def setup_core_routes(app, controller_registry):
    """Setup core system routes"""
    setup_core_config_routes(app, controller_registry)
```

**Core Configuration Routes** (`web/routes/core/config.py`):
- `GET /api/config/profiles` - Get available AWS/GCP profiles
- `GET /api/config` - Get configuration information

### 2. AWS Routes (`/api/aws/*`)

**Module Location**: `web/routes/aws/__init__.py`

```python
# File: web/routes/aws/__init__.py - Lines 10-14
def setup_aws_routes(app, controller_registry):
    """Setup all AWS routes"""
    setup_aws_auth_routes(app, controller_registry)
    setup_aws_resource_routes(app, controller_registry) 
    setup_aws_command_routes(app, controller_registry)
```

**AWS Route Organization:**

#### AWS Authentication Routes (`web/routes/aws/auth.py`)
- `POST /api/aws/auth` - Authenticate with AWS SSO for specified profile
- `POST /api/aws/auth/all` - Authenticate all AWS profiles
- `GET /api/aws/status` - Get AWS authentication status for all profiles
- `GET /api/aws/profiles` - Get available AWS profiles
- `GET /api/aws/identity` - Get current AWS identity (sts get-caller-identity)
- `GET /api/aws/regions` - Get available AWS regions

#### AWS Resource Routes (`web/routes/aws/resources.py`)
- Resource discovery and management endpoints

#### AWS Command Routes (`web/routes/aws/commands.py`)
- Direct AWS CLI command execution endpoints

### 3. GCP Routes (`/api/gcp/*`)

**Module Location**: `web/routes/gcp/__init__.py`

```python
# File: web/routes/gcp/__init__.py - Lines 5-7
def setup_gcp_routes(app, controller_registry):
    """Setup GCP routes - TODO: Extract from main.py"""
    pass
```

**Status**: Routes currently defined in main.py, planned for extraction to organized modules

### 4. Kubernetes Routes (`/api/k8s/*`)

**Module Location**: `web/routes/k8s/__init__.py`

```python
# File: web/routes/k8s/__init__.py - Lines 5-7
def setup_k8s_routes(app, controller_registry):
    """Setup K8s routes - TODO: Extract from main.py"""
    pass
```

**Status**: Routes currently defined in main.py, planned for extraction to organized modules

## 🔄 Route → Controller Integration Pattern

### Standard Route Implementation Pattern

Based on actual implementation from `web/routes/aws/auth.py`:

```python
# File: web/routes/aws/auth.py - Lines 9-34
def setup_aws_auth_routes(app, controller_registry):
    """Setup AWS authentication routes"""
    
    @app.post("/api/aws/auth")
    async def aws_authenticate(request: dict, background_tasks: BackgroundTasks):
        """Authenticate with AWS SSO for specified profile"""
        try:
            profile = request.get('profile', 'dev')
            aws_controller = controller_registry.get_aws_controller()
            
            if aws_controller:
                background_tasks.add_task(
                    aws_controller.authenticate,
                    profile=profile
                )
                return {
                    "success": True,
                    "message": f"WARP-Demo: AWS SSO authentication started for {profile}",
                    "profile": profile
                }
            else:
                return {"success": False, "error": "WARP-Demo: AWS controller not available"}
                
        except Exception as e:
            return {"success": False, "error": f"WARP-Demo: {str(e)}"}
```

### Route Development Pattern

1. **Controller Access**: Get controller from registry
2. **Background Tasks**: Use FastAPI BackgroundTasks for async operations
3. **Error Handling**: Standard try/catch with success/error response format
4. **Response Format**: Consistent JSON response structure

```python
# WARP-Demo: Standard route template
@app.{method}("/api/{provider}/{resource}")
async def {provider}_{resource}_{action}(request: dict, background_tasks: BackgroundTasks):
    """Route description with WARP-Demo markers"""
    try:
        # Step 1: Get controller from registry
        controller = controller_registry.get_{provider}_controller()
        
        if not controller:
            return {"success": False, "error": "WARP-Demo: Controller not available"}
        
        # Step 2: Process request parameters
        params = request.get('params', {})
        
        # Step 3: Execute via controller (background or direct)
        if requires_background:
            background_tasks.add_task(controller.method_name, **params)
            return {
                "success": True, 
                "message": f"WARP-Demo: {action} started",
                "demo_marker": "WARP-Background-Task"
            }
        else:
            result = await controller.method_name(**params)
            return {
                "success": result.get("success", True),
                "data": result,
                "demo_marker": "WARP-Direct-Response"
            }
        
    except Exception as e:
        return {"success": False, "error": f"WARP-Demo: {str(e)}"}
```

## 📋 Current Endpoint Inventory

Based on actual implementation in the codebase:

### Core System Endpoints
- `GET /api/config/profiles` - Available AWS/GCP profiles
- `GET /api/config` - Configuration information
- `GET /api/status` - Global system status (from main.py)

### AWS Provider Endpoints (`/api/aws/*`)
- `POST /api/aws/auth` - AWS SSO authentication
- `POST /api/aws/auth/all` - Authenticate all AWS profiles  
- `GET /api/aws/status` - AWS authentication status
- `GET /api/aws/profiles` - Available AWS profiles
- `GET /api/aws/identity` - Current AWS identity
- `GET /api/aws/regions` - Available AWS regions

### GCP Provider Endpoints (`/api/gcp/*`)
Currently in main.py, planned for extraction:
- `GET /api/gcp/status` - GCP authentication status (from main.py)

### WebSocket Endpoints
- `WS /ws/{client_id}` - WebSocket connection for real-time updates

## 🔍 Dynamic Route Discovery

### Runtime Route Enumeration

```python
# WARP-Demo: Get all routes dynamically
async def discover_all_endpoints():
    """Discover all registered endpoints at runtime"""
    from web.routes import list_all_routes
    from web.main import app  # FastAPI app instance
    
    all_routes = list_all_routes(app)
    
    # Organize routes by provider
    organized_routes = {
        "core": [],
        "aws": [],
        "gcp": [],
        "k8s": [],
        "websocket": []
    }
    
    for route in all_routes:
        path = route['path']
        
        if path.startswith('/api/aws/'):
            organized_routes["aws"].append(route)
        elif path.startswith('/api/gcp/'):
            organized_routes["gcp"].append(route)
        elif path.startswith('/api/k8s/'):
            organized_routes["k8s"].append(route)
        elif path.startswith('/ws/'):
            organized_routes["websocket"].append(route)
        elif path.startswith('/api/'):
            organized_routes["core"].append(route)
    
    return {
        "routes": organized_routes,
        "total_routes": len(all_routes),
        "providers": list(organized_routes.keys()),
        "demo_system": "WARP-Route-Discovery"
    }
```

### Endpoint Auto-Discovery API

```python
# Available via: GET /api/endpoints/all
@app.get("/api/endpoints/all")
async def get_all_endpoints():
    """Auto-discover all available endpoints"""
    routes = list_all_routes(app)
    
    return {
        "success": True,
        "endpoints": routes,
        "count": len(routes),
        "organized_by": "provider",
        "discovery": "automatic",
        "demo_system": "WARP-Endpoint-Discovery"
    }
```

## 🏗️ Route Extension Patterns

### Adding New Provider Routes

```python
# WARP-Demo: Adding Docker provider routes
# File: web/routes/docker/__init__.py

def setup_docker_routes(app, controller_registry):
    """Setup Docker provider routes"""
    
    @app.get("/api/docker/containers")
    async def docker_list_containers(background_tasks: BackgroundTasks):
        """List Docker containers"""
        try:
            docker_controller = controller_registry.get_controller("docker")
            
            if not docker_controller:
                return {"success": False, "error": "WARP-Demo: Docker controller not available"}
            
            background_tasks.add_task(docker_controller.list_containers)
            return {
                "success": True,
                "message": "WARP-Demo: Docker container listing started",
                "provider": "docker"
            }
            
        except Exception as e:
            return {"success": False, "error": f"WARP-Demo: {str(e)}"}

# Update web/routes/__init__.py
def setup_all_routes(app, controller_registry):
    """Setup all routes organized by provider"""
    setup_core_routes(app, controller_registry)
    setup_aws_routes(app, controller_registry)
    setup_gcp_routes(app, controller_registry)
    setup_k8s_routes(app, controller_registry)
    setup_docker_routes(app, controller_registry)  # New provider
```

### Route Capability Organization

```python
# WARP-Demo: Organizing routes by capability within provider
def setup_aws_routes(app, controller_registry):
    """Setup AWS routes organized by capability"""
    
    # Authentication capability
    setup_aws_auth_routes(app, controller_registry)
    
    # Resource management capability
    setup_aws_resource_routes(app, controller_registry)
    
    # Command execution capability  
    setup_aws_command_routes(app, controller_registry)
    
    # Monitoring capability
    setup_aws_monitoring_routes(app, controller_registry)
    
    print("📡 AWS routes organized by capability:")
    print("   - Auth: /api/aws/auth/*")
    print("   - Resources: /api/aws/resources/*")
    print("   - Commands: /api/aws/commands/*")
    print("   - Monitoring: /api/aws/monitoring/*")
```

## 🚨 Route Error Handling Patterns

### Standard Error Response Format

```python
# Standard error handling pattern across all routes
def handle_route_error(error: Exception, context: str = ""):
    """Standard error response with WARP watermarking"""
    return {
        "success": False,
        "error": f"WARP-Demo: {str(error)}",
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "error_type": error.__class__.__name__
    }

# Usage in routes
try:
    # Route logic here
    pass
except Exception as e:
    return handle_route_error(e, "aws_authentication")
```

### Controller Availability Handling

```python
# Standard pattern for controller availability
def get_controller_or_error(controller_registry, controller_name: str):
    """Get controller with standard error handling"""
    controller = controller_registry.get_controller(controller_name)
    
    if not controller:
        return None, {
            "success": False,
            "error": f"WARP-Demo: {controller_name} controller not available",
            "available_controllers": list(controller_registry.list_controllers().keys())
        }
    
    return controller, None
```

## 📊 Route Organization Architecture Benefits

✅ **Provider-Based Organization**: Routes organized by cloud provider for scalability  
✅ **Capability-Based Grouping**: Routes within providers organized by capability  
✅ **Dynamic Discovery**: Runtime enumeration of all available endpoints  
✅ **Controller Integration**: Automatic controller registry integration  
✅ **Background Task Support**: Non-blocking operations via FastAPI BackgroundTasks  
✅ **Consistent Error Handling**: Standard error response format across all routes  
✅ **Extension Pattern**: Clear pattern for adding new provider routes  

## 🧪 Testing Route Organization

### Route Discovery Tests

```bash
# WARP-Demo: Test route discovery functionality
curl http://localhost:8000/api/endpoints/all

# Expected response structure:
{
  "success": true,
  "endpoints": [
    {
      "path": "/api/aws/auth",
      "methods": ["POST"],
      "name": "aws_authenticate"
    },
    {
      "path": "/api/config/profiles",
      "methods": ["GET"],
      "name": "get_available_profiles"
    }
  ],
  "count": 15,
  "organized_by": "provider",
  "demo_system": "WARP-Endpoint-Discovery"
}
```

### Provider Route Tests

```bash
# WARP-Demo: Test AWS provider routes
curl -X POST http://localhost:8000/api/aws/auth \
  -H "Content-Type: application/json" \
  -d '{"profile": "dev"}'

# Test configuration routes
curl http://localhost:8000/api/config/profiles

# Test status routes
curl http://localhost:8000/api/aws/status
```

### Route Organization Validation

```python
# WARP-Demo: Validate route organization
async def validate_route_organization():
    """Validate routes are properly organized by provider"""
    from web.routes import list_all_routes
    from web.main import app
    
    routes = list_all_routes(app)
    providers = {}
    
    for route in routes:
        path = route['path']
        if path.startswith('/api/'):
            provider = path.split('/')[2] if len(path.split('/')) > 2 else 'core'
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(route)
    
    return {
        "validation": "WARP-Demo-Route-Organization",
        "providers": providers,
        "total_providers": len(providers),
        "routes_per_provider": {provider: len(routes) for provider, routes in providers.items()}
    }
```

---

## 📝 Route Organization Documentation Maintenance

**⚠️ CRITICAL: When route organization changes, update this documentation immediately:**

### New Provider Added
- [ ] Create new provider directory in `web/routes/{provider}/`
- [ ] Add `setup_{provider}_routes()` function
- [ ] Update `setup_all_routes()` to include new provider
- [ ] Add provider to endpoint inventory section
- [ ] Update route discovery patterns
- [ ] Test all new routes work correctly

### Route Module Organization Changed
- [ ] Update `setup_{provider}_routes()` method examples
- [ ] Update provider-specific route organization documentation
- [ ] Update endpoint inventory with new routes
- [ ] Test route discovery still works correctly

### Route Implementation Patterns Changed
- [ ] Update standard route template examples
- [ ] Update error handling pattern examples
- [ ] Update controller integration examples
- [ ] Update background task usage patterns

### Dynamic Discovery Changed
- [ ] Update `list_all_routes()` function examples
- [ ] Update endpoint enumeration patterns
- [ ] Update discovery API examples
- [ ] Test route discovery functionality

### Testing Route Organization

```bash
# Test route organization and discovery
cd /Users/warp-demo-user/code/github/apex
python3 web/main.py &

# Test core routes
curl http://localhost:8000/api/config/profiles
curl http://localhost:8000/api/config

# Test AWS routes  
curl -X POST http://localhost:8000/api/aws/auth -H "Content-Type: application/json" -d '{"profile": "dev"}'
curl http://localhost:8000/api/aws/status
curl http://localhost:8000/api/aws/profiles

# Test route discovery
curl http://localhost:8000/api/endpoints/all

kill %1
```

**Documentation Dependencies:**
- **Primary**: `docs/architecture/routes/organization.md` (this file)
- **Secondary**: `docs/architecture/discovery/controllers.md` (controller registry)
- **Implementation**: `web/routes/__init__.py`, route modules in `web/routes/*/`
- **Related**: Controller implementation files

This route organization system enables APEX to scale API endpoints with clear provider-based organization and automatic discovery capabilities.