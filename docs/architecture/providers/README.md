# Providers Layer Documentation

## 🔌 CLI/API Integration with Context Management

The Providers layer handles direct integration with external CLI tools (AWS CLI, gcloud, kubectl) and ensures 100% correct context switching and authentication before command execution.

## 📁 Current Structure

```
apex/web/providers/
├── base_provider.py    # Abstract base class with command execution
├── aws/
│   └── auth.py        # AWS CLI context management & authentication
├── gcp/
│   ├── auth.py        # GCP CLI context management & authentication
│   └── k8s.py         # kubectl context management
└── __init__.py        # Provider registry
```

**Full Paths (from project root):**
- `apex/web/providers/base_provider.py`
- `apex/web/providers/aws/auth.py`
- `apex/web/providers/gcp/auth.py`
- `apex/web/providers/gcp/k8s.py`

## 🎯 Context Management & Authentication Flow

### Core Principle: **Always Pass Environment Context**

Every CLI command execution follows this pattern:
1. **Environment Context Passed**: Controller passes `env` parameter (dev/stage/prod)
2. **Context Mapping**: Provider maps environment to actual CLI context
3. **Context Verification**: Provider verifies current CLI context matches required
4. **Context Switch**: Provider switches CLI context if needed (with authentication)
5. **Command Execution**: Provider executes command with guaranteed correct context
6. **Failure Handling**: Provider fails fast if context cannot be established

### AWS CLI Context Management

#### Environment → Profile Mapping (`apex/web/providers/aws/auth.py`)

```python
# File: apex/web/providers/aws/auth.py
async def execute_aws_command_with_context(self, command: str, env: str = "dev"):
    """Execute AWS command with guaranteed correct profile context"""
    
    # Step 1: Map environment to AWS profile
    profile_mapping = {
        "dev": "dev",
        "stage": "stage", 
        "prod": "prod"
    }
    required_profile = profile_mapping.get(env)
    
    if not required_profile:
        raise ValueError(f"No AWS profile mapping for environment: {env}")
    
    # Step 2: Get current AWS profile context
    current_context = await self.get_current_aws_context()
    
    # Step 3: Context verification and switching
    if current_context != required_profile:
        await self.log_action("aws_context_switch_required", {
            "from_profile": current_context,
            "to_profile": required_profile,
            "env": env
        })
        
        # Step 4: Switch context with authentication check
        success = await self.switch_aws_context(required_profile, env)
        if not success:
            raise RuntimeError(f"Failed to switch AWS context to {required_profile} for {env}")
    
    # Step 5: Execute command with guaranteed context
    full_command = f"aws --profile {required_profile} {command}"
    return await self.execute_command(full_command)

async def get_current_aws_context(self) -> str:
    """Get current AWS profile context"""
    # Check AWS_PROFILE environment variable
    current_profile = os.environ.get('AWS_PROFILE')
    if current_profile:
        return current_profile
    
    # Check default profile from AWS config
    try:
        result = await self.execute_command("aws configure list-profiles")
        if result['success']:
            # Parse current profile from output
            return self.parse_current_profile(result['stdout'])
    except:
        pass
    
    return "default"

async def switch_aws_context(self, profile: str, env: str) -> bool:
    """Switch AWS CLI context to required profile with authentication"""
    
    # Step 1: Check if profile exists
    profile_status = await self.get_profile_status(profile)
    
    # Step 2: If not authenticated, trigger SSO login
    if not profile_status.get('authenticated', False):
        await self.broadcast_message({
            'type': 'aws_auth_required',
            'data': {
                'profile': profile,
                'env': env,
                'message': f'🔐 Authentication required for AWS {profile} (env: {env})'
            }
        })
        
        # Execute SSO login for this profile
        auth_result = await self.authenticate(profile=profile)
        if not auth_result.get('success', False):
            return False
    
    # Step 3: Set AWS_PROFILE environment variable for this session
    os.environ['AWS_PROFILE'] = profile
    
    # Step 4: Verify context switch worked
    verification = await self.verify_aws_context(profile, env)
    if not verification:
        await self.broadcast_message({
            'type': 'aws_context_switch_failed',
            'data': {
                'profile': profile,
                'env': env,
                'error': 'Context verification failed after switch'
            }
        })
        return False
    
    await self.broadcast_message({
        'type': 'aws_context_switched',
        'data': {
            'profile': profile,
            'env': env,
            'message': f'✅ AWS context switched to {profile} for {env}'
        }
    })
    
    return True

async def verify_aws_context(self, expected_profile: str, env: str) -> bool:
    """Verify AWS CLI is using correct context"""
    try:
        # Execute identity check with specific profile
        result = await self.execute_command(f"aws --profile {expected_profile} sts get-caller-identity")
        
        if result['success']:
            identity = json.loads(result['stdout'])
            
            # Verify we got identity from correct account for this environment
            expected_account = self.get_expected_account_for_env(env)
            actual_account = identity.get('Account')
            
            if actual_account == expected_account:
                return True
            else:
                await self.log_action("aws_context_verification_failed", {
                    "expected_account": expected_account,
                    "actual_account": actual_account,
                    "profile": expected_profile,
                    "env": env
                })
                return False
    except Exception as e:
        await self.log_action("aws_context_verification_error", {
            "error": str(e),
            "profile": expected_profile,
            "env": env
        })
        return False
    
    return False
```

### GCP CLI Context Management

#### Environment → Project Mapping (`apex/web/providers/gcp/auth.py`)

```python
# File: apex/web/providers/gcp/auth.py
async def execute_gcp_command_with_context(self, command: str, env: str = "dev"):
    """Execute GCP command with guaranteed correct project context"""
    
    # Step 1: Map environment to GCP project
    project_mapping = {
        "dev": "warp-demo-service-dev",
        "stage": "warp-demo-service-stage",
        "prod": "warp-demo-service-prod"
    }
    required_project = project_mapping.get(env)
    
    if not required_project:
        raise ValueError(f"No GCP project mapping for environment: {env}")
    
    # Step 2: Get current GCP project context
    current_context = await self.get_current_gcp_context()
    
    # Step 3: Context verification and switching
    if current_context != required_project:
        await self.log_action("gcp_context_switch_required", {
            "from_project": current_context,
            "to_project": required_project,
            "env": env
        })
        
        # Step 4: Switch context with authentication check
        success = await self.switch_gcp_context(required_project, env)
        if not success:
            raise RuntimeError(f"Failed to switch GCP context to {required_project} for {env}")
    
    # Step 5: Execute command with guaranteed context
    full_command = f"gcloud --project {required_project} {command}"
    return await self.execute_command(full_command)

async def get_current_gcp_context(self) -> str:
    """Get current GCP project context"""
    try:
        result = await self.execute_command("gcloud config get-value project")
        if result['success'] and result['stdout'].strip():
            return result['stdout'].strip()
    except:
        pass
    
    return "unknown"

async def switch_gcp_context(self, project: str, env: str) -> bool:
    """Switch GCP CLI context to required project with authentication"""
    
    # Step 1: Check if authenticated with gcloud
    auth_status = await self.get_gcp_auth_status()
    
    # Step 2: If not authenticated, trigger auth flow
    if not auth_status.get('authenticated', False):
        await self.broadcast_message({
            'type': 'gcp_auth_required',
            'data': {
                'project': project,
                'env': env,
                'message': f'🔐 Authentication required for GCP {project} (env: {env})'
            }
        })
        
        # Execute gcloud auth login
        auth_result = await self.authenticate(project=project)
        if not auth_result.get('success', False):
            return False
    
    # Step 3: Set active project
    project_result = await self.execute_command(f"gcloud config set project {project}")
    if not project_result['success']:
        return False
    
    # Step 4: Verify context switch worked
    verification = await self.verify_gcp_context(project, env)
    if not verification:
        await self.broadcast_message({
            'type': 'gcp_context_switch_failed',
            'data': {
                'project': project,
                'env': env,
                'error': 'Context verification failed after switch'
            }
        })
        return False
    
    await self.broadcast_message({
        'type': 'gcp_context_switched',
        'data': {
            'project': project,
            'env': env,
            'message': f'✅ GCP context switched to {project} for {env}'
        }
    })
    
    return True
```

### Kubernetes Context Management

#### Environment → Cluster Context Mapping (`apex/web/providers/gcp/k8s.py`)

```python
# File: apex/web/providers/gcp/k8s.py
async def execute_kubectl_command_with_context(self, command: str, env: str = "dev"):
    """Execute kubectl command with guaranteed correct cluster context"""
    
    # Step 1: Map environment to cluster context
    cluster_mapping = {
        "dev": "gke_warp-demo-service-dev_us-central1-a_dev-cluster",
        "stage": "gke_warp-demo-service-stage_us-central1-b_stage-cluster", 
        "prod": "gke_warp-demo-service-prod_us-east1-b_prod-cluster"
    }
    required_context = cluster_mapping.get(env)
    
    if not required_context:
        raise ValueError(f"No kubectl context mapping for environment: {env}")
    
    # Step 2: Get current kubectl context
    current_context = await self.get_current_kubectl_context()
    
    # Step 3: Context verification and switching
    if current_context != required_context:
        await self.log_action("kubectl_context_switch_required", {
            "from_context": current_context,
            "to_context": required_context,
            "env": env
        })
        
        # Step 4: Switch context with authentication check
        success = await self.switch_kubectl_context(required_context, env)
        if not success:
            raise RuntimeError(f"Failed to switch kubectl context to {required_context} for {env}")
    
    # Step 5: Execute command with guaranteed context
    full_command = f"kubectl --context {required_context} {command}"
    return await self.execute_command(full_command)

async def switch_kubectl_context(self, context: str, env: str) -> bool:
    """Switch kubectl context with cluster authentication"""
    
    # Step 1: Ensure GCP authentication for cluster access
    gcp_auth = self.get_provider("gcp_auth")
    if gcp_auth:
        # Get GCP project for this environment
        project = self.get_gcp_project_for_env(env)
        
        # Ensure authenticated with correct GCP project
        await gcp_auth.execute_gcp_command_with_context("auth list", env)
        
        # Get cluster credentials for kubectl
        cluster_info = self.get_cluster_info_for_env(env)
        credentials_cmd = (
            f"container clusters get-credentials {cluster_info['name']} "
            f"--project {project} --zone {cluster_info['zone']}"
        )
        
        creds_result = await gcp_auth.execute_gcp_command_with_context(credentials_cmd, env)
        if not creds_result['success']:
            return False
    
    # Step 2: Switch kubectl context
    switch_result = await self.execute_command(f"kubectl config use-context {context}")
    if not switch_result['success']:
        return False
    
    # Step 3: Verify context switch worked
    verification = await self.verify_kubectl_context(context, env)
    return verification
```

## 🔄 Controller → Provider Context Flow

### How Controllers Always Pass Environment Context

```python
# File: apex/web/controllers/aws_controller.py
async def list_s3_buckets(self, env: str = None, **kwargs) -> Dict[str, Any]:
    """List S3 buckets with guaranteed environment context"""
    
    # Step 1: Ensure environment is specified (never assume)
    env = env or self.current_env
    if not validate_environment(env):
        return {"success": False, "error": f"Invalid environment: {env}"}
    
    # Step 2: Get provider and pass environment context
    aws_auth = self.get_provider("aws_auth")
    if not aws_auth:
        return {"success": False, "error": "AWS provider not available"}
    
    # Step 3: Provider handles context switching automatically
    try:
        result = await aws_auth.execute_aws_command_with_context("s3 ls", env)
        return {"success": True, "buckets": self.parse_s3_buckets(result['stdout'])}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## ⚠️ Failure Handling: Fail Fast on Context Issues

### Context Switch Failures

```python
async def handle_context_failure(self, provider: str, required_context: str, env: str, error: str):
    """Handle context switch failures - fail fast with clear error"""
    
    error_message = f"❌ {provider.upper()} context switch failed: Cannot switch to {required_context} for {env}"
    
    await self.broadcast_message({
        'type': 'context_switch_failure',
        'data': {
            'provider': provider,
            'required_context': required_context,
            'env': env,
            'error': error,
            'message': error_message,
            'action_required': f'Please authenticate {provider} for {env} environment'
        }
    })
    
    # Log for debugging
    await self.log_action("context_switch_failure", {
        "provider": provider,
        "required_context": required_context,
        "env": env,
        "error": error
    })
    
    # Fail fast - don't continue with wrong context
    raise RuntimeError(error_message)
```

### Authentication Failures

```python
async def handle_auth_failure(self, provider: str, context: str, env: str):
    """Handle authentication failures - fail fast"""
    
    error_message = f"❌ {provider.upper()} authentication failed for {context} (env: {env})"
    
    await self.broadcast_message({
        'type': 'auth_failure', 
        'data': {
            'provider': provider,
            'context': context,
            'env': env,
            'message': error_message,
            'action_required': f'Run: {self.get_manual_auth_command(provider, context)}'
        }
    })
    
    raise RuntimeError(error_message)
```

## 📊 Context State Management

### Provider State Tracking

```python
class BaseProvider:
    def __init__(self, name: str):
        self.name = name
        self.current_contexts = {
            'last_verified_env': None,
            'last_verified_context': None,
            'last_verification_time': None
        }
    
    async def track_context_state(self, env: str, context: str):
        """Track current context state for efficiency"""
        self.current_contexts.update({
            'last_verified_env': env,
            'last_verified_context': context,
            'last_verification_time': time.time()
        })
    
    def needs_context_verification(self, env: str) -> bool:
        """Check if context verification is needed"""
        # Always verify if environment changed
        if self.current_contexts['last_verified_env'] != env:
            return True
        
        # Verify periodically (every 5 minutes)
        last_check = self.current_contexts['last_verification_time']
        if not last_check or (time.time() - last_check) > 300:
            return True
            
        return False
```

## 🧪 Testing Context Management

### Testing Context Switching

```bash
# Test AWS context switching
curl -X POST http://localhost:8000/api/aws/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "s3 ls", "environment": "dev"}'

# Verify correct profile used in logs
curl -X POST http://localhost:8000/api/aws/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "s3 ls", "environment": "prod"}'

# Should see context switch messages in WebSocket stream
```

---

## 📝 Documentation Maintenance Instructions

**⚠️ When CLI context management changes, update this documentation immediately:**

### Context Mapping Changes
- [ ] Update environment → profile/project/context mappings
- [ ] Update `get_current_{provider}_context()` examples
- [ ] Update verification logic examples  
- [ ] Test all context switches work with real CLIs

### Authentication Flow Changes
- [ ] Update authentication trigger examples
- [ ] Update failure handling patterns
- [ ] Update WebSocket message examples
- [ ] Verify error messages match actual implementation

### New Provider Added
- [ ] Add context management section for new provider
- [ ] Add environment mapping examples
- [ ] Add authentication flow examples
- [ ] Add verification and failure handling

### Testing Context Management
```bash
# Verify context management works
cd apex/
python3 apex.py --web &

# Test context switching between environments
curl -X POST http://localhost:8000/api/aws/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "sts get-caller-identity", "environment": "dev"}'

curl -X POST http://localhost:8000/api/aws/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "sts get-caller-identity", "environment": "prod"}'

# Should see different account IDs, indicating context switch worked
kill %1
```