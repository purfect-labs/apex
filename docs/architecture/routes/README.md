# Routes Layer Documentation

## 🌐 HTTP Endpoint Definitions & Request Handling

The Routes layer handles HTTP request routing and delegates to Controllers for business logic.

## 📁 Current Structure

```
apex/web/routes/
├── aws/
│   ├── auth.py      # AWS authentication endpoints
│   ├── commands.py  # AWS command execution
│   └── resources.py # AWS resource management
├── gcp/             # (planned)
└── k8s/             # (planned)
```

**Full Paths (from project root):**
- `apex/web/routes/aws/auth.py`
- `apex/web/routes/aws/commands.py` 
- `apex/web/routes/aws/resources.py`

## 🔗 Route → Controller Flow Pattern

### Standard Pattern
```python
@app.get("/api/{service}/{action}")
async def endpoint_name(params):
    """Route: Parse request, call controller"""
    controller = controller_registry.get_{service}_controller()
    if controller:
        return await controller.method_name(params)
    else:
        return {"success": False, "error": "Controller not available"}
```

## 📋 AWS Routes Specification

### Authentication Routes (`apex/web/routes/aws/auth.py`)

#### POST /api/aws/auth
```python
@app.post("/api/aws/auth")
async def aws_authenticate(request: dict, background_tasks: BackgroundTasks):
    profile = request.get('profile', 'dev')
    aws_controller = controller_registry.get_aws_controller()
    
    background_tasks.add_task(
        aws_controller.authenticate,
        profile=profile
    )
    
    return {
        "success": True,
        "message": f"AWS SSO authentication started for {profile}",
        "profile": profile
    }
```

**Real Usage:**
```bash
curl -X POST http://localhost:8000/api/aws/auth \
  -H "Content-Type: application/json" \
  -d '{"profile": "dev"}'
```

#### GET /api/aws/status
```python
@app.get("/api/aws/status")
async def aws_status():
    aws_controller = controller_registry.get_aws_controller()
    return await aws_controller.get_status()
```

**Response Example:**
```json
{
  "profiles": {
    "dev": {
      "authenticated": true,
      "account": "111111111111",
      "user": "user@example.com"
    }
  },
  "all_authenticated": true
}
```

#### GET /api/aws/profiles
```python
@app.get("/api/aws/profiles")
async def aws_profiles():
    aws_controller = controller_registry.get_aws_controller()
    return await aws_controller.list_aws_profiles()
```

#### GET /api/aws/identity
```python
@app.get("/api/aws/identity")
async def aws_identity(env: str = "dev"):
    aws_controller = controller_registry.get_aws_controller()
    return await aws_controller.get_current_identity(env=env)
```

### Command Routes (`apex/web/routes/aws/commands.py`)

#### POST /api/aws/execute
```python
@app.post("/api/aws/execute")
async def aws_execute_command(request: dict, background_tasks: BackgroundTasks):
    command = request.get('command', '')
    environment = request.get('environment', 'dev')
    
    aws_controller = controller_registry.get_aws_controller()
    background_tasks.add_task(
        aws_controller.execute_aws_command,
        command=command,
        env=environment
    )
    
    return {
        "success": True,
        "message": f"AWS command execution started: {command}",
        "command": command,
        "environment": environment
    }
```

**Real Usage:**
```bash
curl -X POST http://localhost:8000/api/aws/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "s3 ls", "environment": "dev"}'
```

### Resource Routes (`apex/web/routes/aws/resources.py`)

#### GET /api/aws/endpoints
```python
@app.get("/api/aws/endpoints")
async def aws_endpoints():
    aws_controller = controller_registry.get_aws_controller()
    return await aws_controller.get_endpoints()
```

## 📝 Route Registration Pattern

Routes are registered in `apex/web/main.py`:

```python
# File: apex/web/main.py
# Setup route modules
from .routes.aws import auth, commands, resources

def setup_routes(self):
    """Register all route modules"""
    auth.setup_aws_auth_routes(self.app, self.controller_registry)
    commands.setup_aws_command_routes(self.app, self.controller_registry)
    resources.setup_aws_resource_routes(self.app, self.controller_registry)
```

## 🔧 Route Development Pattern

### Adding New Route
1. **Create route function in appropriate module**
2. **Follow standard error handling pattern**
3. **Use background tasks for long-running operations**
4. **Register in setup function**

### Standard Route Template
```python
@app.{method}("/api/{service}/{action}")
async def {service}_{action}({params}):
    """Route description"""
    try:
        controller = controller_registry.get_{service}_controller()
        
        if not controller:
            return {"success": False, "error": "{Service} controller not available"}
        
        # For async operations
        if background_tasks:
            background_tasks.add_task(controller.method_name, **params)
            return {"success": True, "message": "Operation started"}
        
        # For sync operations  
        return await controller.method_name(**params)
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## 🚨 Error Handling Patterns

### Controller Not Available
```python
if not controller:
    return {"success": False, "error": "AWS controller not available"}
```

### Exception Handling
```python
try:
    return await controller.method_name()
except Exception as e:
    return {"success": False, "error": str(e)}
```

### Background Task Response
```python
background_tasks.add_task(controller.long_operation)
return {
    "success": True,
    "message": "Operation initiated",
    "task_id": task_id  # Optional
}
```

## 🔄 WebSocket Integration

Routes don't directly handle WebSocket connections, but they trigger operations that stream via WebSocket:

```python
# Route triggers background task
background_tasks.add_task(controller.streaming_operation)

# Controller broadcasts via WebSocket
await self.broadcast_message({
    'type': 'command_output',
    'data': {'output': result, 'context': 'aws'}
})
```

## 📊 Request/Response Standards

### Request Format
```json
{
  "action": "authenticate",
  "provider": "aws",
  "profile": "dev",
  "parameters": {}
}
```

### Success Response
```json
{
  "success": true,
  "message": "Operation completed",
  "data": {...}
}
```

### Error Response
```json
{
  "success": false,
  "error": "Specific error message"
}
```

## 🧪 Testing Routes

### Direct Route Testing
```bash
# Test authentication
curl -X POST http://localhost:8000/api/aws/auth \
  -H "Content-Type: application/json" \
  -d '{"profile": "dev"}'

# Test status
curl http://localhost:8000/api/aws/status

# Test command execution
curl -X POST http://localhost:8000/api/aws/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "sts get-caller-identity", "environment": "dev"}'
```

### Playwright Testing
```javascript
// Test route via UI
test('AWS authentication route', async ({ page }) => {
  await page.goto('http://localhost:8000');
  await page.click('[data-action="auth-aws"]');
  
  // Should trigger POST /api/aws/auth
  const response = await page.waitForResponse('/api/aws/auth');
  expect(response.ok()).toBeTruthy();
});
```

---

## 📝 Documentation Maintenance Instructions

**⚠️ When Routes change, update this documentation immediately:**

### New Route Added
1. **Update Route Specification Section**
   - Add new route to appropriate service section (AWS/GCP/K8s)
   - Include full function signature with file path comment
   - Add curl example with real usage
   - Include response example with actual data

2. **Update File Structure**
   - Add new route files to "Current Structure" section
   - Update "Full Paths" list with new files
   - Verify relative paths from project root (`apex/...`)

3. **Update Registration Pattern**
   - Add new route setup call to `apex/web/main.py` example
   - Show how new route module is imported

### Route Modified
1. **Update Function Examples**
   - Change function signatures to match actual code
   - Update parameter examples to reflect real usage
   - Fix response examples to show actual return format

2. **Update curl Examples**
   - Test actual curl commands work with current server
   - Update request/response JSON to match real behavior
   - Verify endpoint URLs are correct

3. **Update Error Handling**
   - Check error response formats match actual implementation
   - Update error message examples

### Route Removed
1. **Remove from Documentation**
   - Delete route specification section
   - Remove from file structure and paths list
   - Remove from registration example
   - Remove from testing examples

2. **Update Navigation**
   - Remove links to deleted sections
   - Update table of contents if present

### Validation Checklist
After updating Routes documentation:

- [ ] All file paths use relative format from project root (`apex/...`)
- [ ] All code examples include file path comments (`# File: apex/web/routes/...`)
- [ ] All curl examples tested against running server
- [ ] All response examples contain real data (no placeholder values)
- [ ] All route functions match actual implementation signatures
- [ ] Registration patterns in `apex/web/main.py` are current
- [ ] Error handling examples reflect actual error responses
- [ ] WebSocket integration examples are accurate
- [ ] Testing examples (curl + Playwright) are functional

### Files to Keep Updated
**Primary:** `apex/docs/architecture/routes/README.md` (this file)
**Secondary:**
- `apex/docs/architecture/README.md` (master doc route references)
- Route implementation files as they change
- Testing files that reference routes

### Testing Documentation Changes
```bash
# Test all curl examples work
cd apex/
python3 apex.py --web &  # Start server

# Test each curl example from documentation
curl -X POST http://localhost:8000/api/aws/auth \
  -H "Content-Type: application/json" \
  -d '{"profile": "dev"}'

# Verify response matches documented examples
# Kill server when done
kill %1
```
```