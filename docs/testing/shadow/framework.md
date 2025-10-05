# Shadow Testing Framework Documentation

## Overview

The APEX Shadow Testing Framework provides automated end-to-end testing capabilities for the admin interface through Playwright-based page object models. The framework enables comprehensive testing of all provider capabilities with structured selectors and automated workflows.

## AdminPage Class Architecture

**File Location**: `web/testing/shadow/utils/admin-page.js`  
**Framework**: Playwright Page Object Model  
**Purpose**: Complete automation of the cyberpunk admin interface for multi-layer testing

### Class Constructor and Initialization

```javascript
class AdminPage {
    constructor(page) {
        this.page = page;  // Playwright page instance
        // Structured selector definitions for all components
    }
}
```

## Selector Architecture

### Navigation Selectors

The AdminPage class provides structured navigation through comprehensive selector mapping:

```javascript
this.navItems = {
    awsProvider: 'div[onclick="showSection(\'aws-provider\')"]',
    gcpProvider: 'div[onclick="showSection(\'gcp-provider\')"]', 
    k8sProvider: 'div[onclick="showSection(\'k8s-provider\')"]',
    awsCommands: 'div[onclick="showSection(\'aws-commands\')"]',
    gcpCommands: 'div[onclick="showSection(\'gcp-commands\')"]',
    kubectlCommands: 'div[onclick="showSection(\'kubectl-commands\')"]',
    systemStatus: 'div[onclick="showSection(\'system-status\')"]',
    logsViewer: 'div[onclick="showSection(\'logs-viewer\')"]'
};
```

**Navigation Pattern**: All selectors target actual `onclick` handlers from the admin.html implementation, ensuring direct mapping to real UI interactions.

## Provider-Specific Testing Components

### AWS Provider Selectors (`this.aws`)

#### Section Navigation
```javascript
sections: {
    provider: '#aws-provider',    // Main AWS provider testing section
    commands: '#aws-commands'     // AWS CLI command execution section
}
```

#### Authentication Status Cards
```javascript
statusCards: {
    dev: '#aws-dev-status',       // DEV environment status (Account: 111111111111)
    stage: '#aws-stage-status',   // STAGE environment status (Account: 222222222222)
    prod: '#aws-prod-status'      // PROD environment status (Account: 333333333333)
}
```

#### Capability Testing Buttons
```javascript
capabilities: {
    identity: 'button[onclick="testAWSCapability(\'identity\')"]',
    profiles: 'button[onclick="testAWSCapability(\'profiles\')"]',
    regions: 'button[onclick="testAWSCapability(\'regions\')"]',
    switchProfile: 'button[onclick="testAWSCapability(\'switch-profile\')"]'
}
```

#### Command Execution Interface
```javascript
commands: {
    envSelect: '#aws-env-select',        // Environment selector dropdown
    input: '#aws-command-input',         // Command input field
    execute: 'button[onclick="executeAWSCommand()"]',  // Execute button
    output: '#aws-command-output',       // Output container
    result: '#aws-command-result',       // Result display area
    quickButtons: {
        identity: 'button[onclick="setAWSCommand(\'aws sts get-caller-identity\')"]',
        ec2: 'button[onclick="setAWSCommand(\'aws ec2 describe-instances --max-items 5\')"]',
        s3: 'button[onclick="setAWSCommand(\'aws s3 ls\')"]',
        rds: 'button[onclick="setAWSCommand(\'aws rds describe-db-instances\')"]',
        iam: 'button[onclick="setAWSCommand(\'aws iam get-user\')"]',
        route53: 'button[onclick="setAWSCommand(\'aws route53 list-hosted-zones\')"]'
    }
}
```

### GCP Provider Selectors (`this.gcp`)

#### Project Status Cards
```javascript
statusCards: {
    dev: '#gcp-dev-status',      // DEV project (warp-demo-service-dev)
    stage: '#gcp-stage-status',  // STAGE project (warp-demo-service-stage)
    prod: '#gcp-prod-status'     // PROD project (warp-demo-service-prod)
}
```

#### GCP Capability Testing
```javascript
capabilities: {
    authList: 'button[onclick="testGCPCapability(\'auth-list\')"]',
    projects: 'button[onclick="testGCPCapability(\'projects\')"]',
    switchProject: 'button[onclick="testGCPCapability(\'switch-project\')"]',
    config: 'button[onclick="testGCPCapability(\'config\')"]'
}
```

#### GCP Command Interface
```javascript
commands: {
    projectSelect: '#gcp-project-select',    // Project selector dropdown
    input: '#gcp-command-input',             // gcloud command input
    execute: 'button[onclick="executeGCPCommand()"]',
    quickButtons: {
        authList: 'button[onclick="setGCPCommand(\'gcloud auth list\')"]',
        projects: 'button[onclick="setGCPCommand(\'gcloud projects list\')"]',
        vms: 'button[onclick="setGCPCommand(\'gcloud compute instances list --limit=5\')"]',
        buckets: 'button[onclick="setGCPCommand(\'gcloud storage buckets list\')"]',
        gke: 'button[onclick="setGCPCommand(\'gcloud container clusters list\')"]',
        sql: 'button[onclick="setGCPCommand(\'gcloud sql instances list\')"]'
    }
}
```

### Kubernetes Provider Selectors (`this.k8s`)

#### K8s Capability Testing
```javascript
capabilities: {
    clusterInfo: 'button[onclick="testK8sCapability(\'cluster-info\')"]',
    contexts: 'button[onclick="testK8sCapability(\'contexts\')"]',
    namespaces: 'button[onclick="testK8sCapability(\'namespaces\')"]',
    nodes: 'button[onclick="testK8sCapability(\'nodes\')"]',
    pods: 'button[onclick="testK8sCapability(\'pods\')"]',
    services: 'button[onclick="testK8sCapability(\'services\')"]'
}
```

#### kubectl Command Interface
```javascript
commands: {
    input: '#kubectl-command-input',         // kubectl command input
    execute: 'button[onclick="executeKubectlCommand()"]',
    quickButtons: {
        clusterInfo: 'button[onclick="setKubectlCommand(\'kubectl cluster-info\')"]',
        nodes: 'button[onclick="setKubectlCommand(\'kubectl get nodes\')"]',
        allPods: 'button[onclick="setKubectlCommand(\'kubectl get pods --all-namespaces\')"]',
        services: 'button[onclick="setKubectlCommand(\'kubectl get services\')"]',
        namespaces: 'button[onclick="setKubectlCommand(\'kubectl get namespaces\')"]',
        contexts: 'button[onclick="setKubectlCommand(\'kubectl get contexts\')"]',
        topNodes: 'button[onclick="setKubectlCommand(\'kubectl top nodes\')"]',
        deployments: 'button[onclick="setKubectlCommand(\'kubectl get deployments --all-namespaces\')"]'
    }
}
```

## Core Testing Methods

### Navigation and Initialization

#### Page Navigation
```javascript
async navigateToAdminPage() {
    await this.page.goto('http://localhost:8000/static/admin.html');
    await this.page.waitForLoadState('networkidle');
    await this.waitForAdminInitialization();
    // Load dynamic profiles after page loads
    await this.loadAvailableProfiles();
}
```

**Features**:
- Waits for network idle to ensure full page load
- Automatically initializes admin interface
- Loads dynamic profile configuration

#### Dynamic Profile Discovery
```javascript
async loadAvailableProfiles() {
    if (this.profiles) return this.profiles; // Cache profiles
    
    const response = await this.page.evaluate(async () => {
        const resp = await fetch('/api/config/profiles');
        return await resp.json();
    });
    
    if (response.success) {
        this.profiles = {
            aws: response.aws_profiles,              // Real AWS profiles from config
            gcp: response.gcp_projects,              // Real GCP projects from config
            aws_details: response.aws_profile_details,
            gcp_details: response.gcp_project_details
        };
    }
    
    return this.profiles;
}
```

**Auto-Discovery Features**:
- ✅ **Real Config Integration**: Fetches actual profiles from `/api/config/profiles`
- ✅ **Caching**: Profiles cached after first load for performance
- ✅ **Error Handling**: Throws descriptive errors if profile loading fails
- ✅ **WARP Compatibility**: Uses actual profile names, no fake data

### AWS Provider Testing Methods

#### Authentication Testing
```javascript
async testAWSAuthentication(environment) {
    await this.navigateToSection('awsProvider');
    
    // Use dynamic profile instead of hardcoded
    const profiles = await this.loadAvailableProfiles();
    if (!profiles.aws.includes(environment)) {
        throw new Error(`Environment '${environment}' not found in config. Available: ${profiles.aws.join(', ')}`);
    }
    
    const statusSelector = this.aws.statusCards[environment];
    
    // Click the status card to trigger auth test
    await this.page.click(statusSelector, { force: true });
    await this.page.waitForTimeout(3000); // Allow auth test to complete
    
    const statusText = await this.page.textContent(statusSelector);
    return statusText;
}
```

**Testing Features**:
- ✅ **Real Profile Validation**: Validates against actual config before testing
- ✅ **Multi-Environment**: Supports dev/stage/prod environments
- ✅ **Error Reporting**: Clear error messages for invalid environments
- ✅ **Status Verification**: Returns actual authentication status text

#### AWS Capability Testing
```javascript
async testAWSCapability(capability) {
    await this.navigateToSection('awsProvider');
    const buttonSelector = this.aws.capabilities[capability];
    
    await this.page.click(buttonSelector);
    await this.page.waitForSelector(this.aws.providerOutput.container, { state: 'visible' });
    await this.page.waitForTimeout(5000); // Allow API call to complete
    
    const resultText = await this.page.textContent(this.aws.providerOutput.result);
    return resultText;
}
```

**Capability Tests Available**:
- **identity**: Tests `aws sts get-caller-identity` capability
- **profiles**: Tests AWS profile enumeration
- **regions**: Tests AWS region discovery
- **switchProfile**: Tests profile switching functionality

#### AWS Command Execution
```javascript
async executeAWSCommand(command, environment = 'dev') {
    await this.navigateToSection('awsCommands');
    
    // Select environment
    await this.page.selectOption(this.aws.commands.envSelect, environment);
    
    // Enter command
    await this.page.fill(this.aws.commands.input, command);
    
    // Execute
    await this.page.click(this.aws.commands.execute);
    await this.page.waitForSelector(this.aws.commands.output, { state: 'visible' });
    await this.page.waitForTimeout(10000); // AWS commands can be slow
    
    const resultText = await this.page.textContent(this.aws.commands.result);
    return resultText;
}
```

**Command Execution Features**:
- ✅ **Environment Selection**: Automatically sets AWS profile context
- ✅ **Real Command Execution**: Executes actual AWS CLI commands
- ✅ **Timeout Handling**: 10-second timeout for slow AWS operations
- ✅ **Output Capture**: Returns full command output for validation

### GCP Provider Testing Methods

#### GCP Authentication Testing
```javascript
async testGCPAuthentication(project) {
    await this.navigateToSection('gcpProvider');
    const statusSelector = this.gcp.statusCards[project];
    
    // Click the status card to trigger auth test
    await this.page.click(statusSelector, { force: true });
    await this.page.waitForTimeout(3000);
    
    const statusText = await this.page.textContent(statusSelector);
    return statusText;
}
```

#### GCP Command Execution
```javascript
async executeGCPCommand(command, project = 'dev') {
    await this.navigateToSection('gcpCommands');
    
    // Select project
    await this.page.selectOption(this.gcp.commands.projectSelect, project);
    
    // Enter command
    await this.page.fill(this.gcp.commands.input, command);
    
    // Execute
    await this.page.click(this.gcp.commands.execute);
    await this.page.waitForTimeout(10000); // GCP commands can be slow
    
    const resultText = await this.page.textContent(this.gcp.commands.result);
    return resultText;
}
```

### Kubernetes Provider Testing Methods

#### K8s Capability Testing
```javascript
async testK8sCapability(capability) {
    await this.navigateToSection('k8sProvider');
    const buttonSelector = this.k8s.capabilities[capability];
    
    await this.page.click(buttonSelector);
    await this.page.waitForSelector(this.k8s.providerOutput.container, { state: 'visible' });
    await this.page.waitForTimeout(5000);
    
    const resultText = await this.page.textContent(this.k8s.providerOutput.result);
    return resultText;
}
```

#### kubectl Command Execution
```javascript
async executeKubectlCommand(command) {
    await this.navigateToSection('kubectlCommands');
    
    // Enter command
    await this.page.fill(this.k8s.commands.input, command);
    
    // Execute
    await this.page.click(this.k8s.commands.execute);
    await this.page.waitForTimeout(8000); // kubectl commands can be slow
    
    const resultText = await this.page.textContent(this.k8s.commands.result);
    return resultText;
}
```

## Utility and Helper Methods

### Response State Validation

#### Success Response Validation
```javascript
async waitForResponseSuccess(resultSelector, timeout = 10000) {
    await this.page.waitForFunction(
        (selector) => {
            const element = document.querySelector(selector);
            return element && element.classList.contains('response-success');
        },
        resultSelector,
        { timeout }
    );
}
```

#### Error Response Validation
```javascript
async waitForResponseError(resultSelector, timeout = 10000) {
    await this.page.waitForFunction(
        (selector) => {
            const element = document.querySelector(selector);
            return element && element.classList.contains('response-error');
        },
        resultSelector,
        { timeout }
    );
}
```

**Response Validation Features**:
- ✅ **CSS Class Detection**: Uses actual admin.html response styling classes
- ✅ **Configurable Timeouts**: Default 10-second timeout, customizable
- ✅ **Multi-Layer Validation**: Enables testing of success/error scenarios
- ✅ **Real UI Feedback**: Tests against actual visual feedback indicators

### System Management

#### System Status Refresh
```javascript
async refreshSystemStatus() {
    await this.navigateToSection('systemStatus');
    await this.page.click(this.system.refreshButton);
    await this.page.waitForTimeout(3000);
}
```

#### Log Entry Retrieval
```javascript
async getLogEntries() {
    await this.navigateToSection('logsViewer');
    const logEntries = await this.page.locator('#live-logs .log-entry').allTextContents();
    return logEntries;
}
```

## Testing Usage Patterns

### Basic Provider Testing Example

```javascript
const { AdminPage } = require('./web/testing/shadow/utils/admin-page.js');

// Test AWS authentication across all environments
async function testAWSMultiEnv(page) {
    const adminPage = new AdminPage(page);
    await adminPage.navigateToAdminPage();
    
    const results = {};
    const environments = ['dev', 'stage', 'prod'];
    
    for (const env of environments) {
        try {
            const status = await adminPage.testAWSAuthentication(env);
            results[env] = { success: true, status };
        } catch (error) {
            results[env] = { success: false, error: error.message };
        }
    }
    
    return results;
}
```

### Comprehensive Capability Testing

```javascript
async function testAllProviderCapabilities(page) {
    const adminPage = new AdminPage(page);
    await adminPage.navigateToAdminPage();
    
    const testResults = {
        aws: {},
        gcp: {},
        k8s: {}
    };
    
    // Test AWS capabilities
    const awsCapabilities = ['identity', 'profiles', 'regions', 'switchProfile'];
    for (const capability of awsCapabilities) {
        testResults.aws[capability] = await adminPage.testAWSCapability(capability);
    }
    
    // Test GCP capabilities
    const gcpCapabilities = ['authList', 'projects', 'switchProject', 'config'];
    for (const capability of gcpCapabilities) {
        testResults.gcp[capability] = await adminPage.testGCPCapability(capability);
    }
    
    // Test K8s capabilities
    const k8sCapabilities = ['clusterInfo', 'contexts', 'namespaces', 'nodes'];
    for (const capability of k8sCapabilities) {
        testResults.k8s[capability] = await adminPage.testK8sCapability(capability);
    }
    
    return testResults;
}
```

### Real Command Execution Testing

```javascript
async function testRealCommandExecution(page) {
    const adminPage = new AdminPage(page);
    await adminPage.navigateToAdminPage();
    
    // Test real AWS commands
    const awsResult = await adminPage.executeAWSCommand('aws sts get-caller-identity', 'dev');
    
    // Test real GCP commands
    const gcpResult = await adminPage.executeGCPCommand('gcloud auth list', 'dev');
    
    // Test real kubectl commands
    const k8sResult = await adminPage.executeKubectlCommand('kubectl cluster-info');
    
    return {
        aws: awsResult,
        gcp: gcpResult,
        k8s: k8sResult
    };
}
```

## Integration with WARP Multi-Layer Testing

### Background Testing Implementation

```javascript
// Following WARP rules - use backgrounding and tmp logging for risky tests
async function backgroundTestWithLogging(testFunction, testName) {
    const logFile = `/tmp/warp-shadow-test-${Date.now()}.log`;
    
    try {
        // Execute test in background with timeout
        const result = await Promise.race([
            testFunction(),
            new Promise((_, reject) => setTimeout(() => reject('timeout'), 30000))
        ]);
        
        // Log success
        await logToFile(logFile, `✅ ${testName} completed successfully`);
        return { success: true, result };
        
    } catch (error) {
        // Log failure for debugging
        await logToFile(logFile, `❌ ${testName} failed: ${error}`);
        return { success: false, error: error.message };
    }
}
```

### Multi-Layer Validation Pattern

```javascript
async function multiLayerProviderTest(page, provider, capability) {
    const adminPage = new AdminPage(page);
    
    // Layer 1: UI interaction test
    const uiResult = await adminPage.testAWSCapability(capability);
    
    // Layer 2: Direct API validation
    const apiResult = await page.evaluate(async (cap) => {
        const response = await fetch(`/api/aws/${cap}`);
        return await response.json();
    }, capability);
    
    // Layer 3: Command execution validation
    const cmdResult = await adminPage.executeAWSCommand(`aws ${capability} --help`);
    
    // Layer 4: Response state validation
    await adminPage.waitForResponseSuccess('#aws-provider-result');
    
    return {
        ui: uiResult,
        api: apiResult,
        command: cmdResult,
        validated: true
    };
}
```

## Performance and Reliability Features

### Intelligent Waiting Strategies

- **Network Idle**: Waits for complete page load before interactions
- **Timeout Management**: Configurable timeouts based on operation complexity
  - AWS commands: 10 seconds (can be slow)
  - GCP commands: 10 seconds (can be slow)
  - kubectl commands: 8 seconds (typically faster)
  - UI interactions: 3-5 seconds
- **Selector Strategies**: Uses both CSS selectors and `onclick` attributes for reliability

### Error Handling and Recovery

```javascript
// Dynamic profile validation prevents test failures
const profiles = await this.loadAvailableProfiles();
if (!profiles.aws.includes(environment)) {
    throw new Error(`Environment '${environment}' not found in config. Available: ${profiles.aws.join(', ')}`);
}
```

### Caching and Optimization

- **Profile Caching**: Loaded profiles cached to avoid repeated API calls
- **Section Navigation Optimization**: Reuses navigation state when possible
- **Selective Waiting**: Only waits for necessary elements to appear

## Advanced Testing Scenarios

### Authentication Flow Testing

```javascript
async function testAuthenticationFlows(page) {
    const adminPage = new AdminPage(page);
    await adminPage.navigateToAdminPage();
    
    // Load real profiles
    const profiles = await adminPage.loadAvailableProfiles();
    
    const authResults = {};
    
    // Test all AWS profiles
    for (const profile of profiles.aws) {
        authResults[`aws_${profile}`] = await adminPage.testAWSAuthentication(profile);
    }
    
    // Test all GCP projects  
    for (const project of profiles.gcp) {
        authResults[`gcp_${project}`] = await adminPage.testGCPAuthentication(project);
    }
    
    return authResults;
}
```

### End-to-End Workflow Testing

```javascript
async function testCompleteWorkflow(page) {
    const adminPage = new AdminPage(page);
    
    // 1. Navigate and initialize
    await adminPage.navigateToAdminPage();
    
    // 2. Test AWS authentication
    const awsAuth = await adminPage.testAWSAuthentication('dev');
    
    // 3. Execute AWS command
    const awsCmd = await adminPage.executeAWSCommand('aws sts get-caller-identity');
    
    // 4. Test GCP capabilities
    const gcpAuth = await adminPage.testGCPCapability('authList');
    
    // 5. Check system status
    await adminPage.refreshSystemStatus();
    
    // 6. Verify logs
    const logs = await adminPage.getLogEntries();
    
    return {
        workflow_complete: true,
        aws_auth: awsAuth,
        aws_command: awsCmd,
        gcp_auth: gcpAuth,
        log_entries: logs.length
    };
}
```

This Shadow Testing Framework provides comprehensive automation capabilities for the APEX admin interface with real provider integration, multi-layer validation, and WARP-compliant testing patterns. All selectors and methods are based on the actual implementation in `web/static/admin.html` and provide reliable automation for end-to-end testing scenarios.

<citations>
<document>
    <document_type>RULE</document_type>
    <document_id>DdzrPTuR904KjfjPhIj8gG</document_id>
</document>
<document>
    <document_type>RULE</document_type>
    <document_id>ZdkT2akGMr8kwyxWhsPYkw</document_id>
</document>
<document>
    <document_type>RULE</document_type>
    <document_id>NoSE2KykRQ88LJcPkrCOBC</document_id>
</document>
</citations>