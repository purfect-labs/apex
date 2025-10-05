# APEX Shadow Testing Framework

A comprehensive end-to-end testing framework that validates provider layer capabilities through the admin UI interface without intermediate fake pages.

## 🎯 Overview

The Shadow Testing Framework provides modular, provider-specific testing for APEX's cloud provider integrations:
- **AWS Provider Testing**: Authentication, environments, capabilities, commands
- **GCP Provider Testing**: Authentication, projects, capabilities, commands  
- **Kubernetes Provider Testing**: Cluster connectivity, kubectl commands, contexts

## 📁 Directory Structure

```
web/testing/shadow/
├── README.md                           # This documentation
├── run-shadow-tests.sh                 # Main test runner script
├── shadow-test.config.js               # Playwright configuration
├── shadow-reports/                     # Test results and reports
├── utils/
│   └── admin-page.js                   # Page Object Model for admin UI
└── tests/
    ├── aws-provider.shadow.spec.js     # AWS provider tests
    ├── gcp-provider.shadow.spec.js     # GCP provider tests
    └── kubernetes-provider.shadow.spec.js # Kubernetes provider tests
```

## 🚀 Quick Start

### Prerequisites

1. **APEX Server Running**: The admin interface must be accessible
   ```bash
   cd /Users/shawn_meredith/code/github/apex
   python3 apex.py --web
   ```

2. **Node.js & Playwright**: Required for test execution
   ```bash
   npm install @playwright/test
   npx playwright install chromium
   ```

### Running Tests

**All Provider Tests (Parallel - 6 Workers):**
```bash
./run-shadow-tests.sh parallel  # Fastest execution
./run-shadow-tests.sh all       # Same as parallel
```

**Specific Provider (Parallel):**
```bash
./run-shadow-tests.sh aws        # AWS with 6 workers
./run-shadow-tests.sh gcp        # GCP with 6 workers
./run-shadow-tests.sh kubernetes # K8s with 6 workers
```

**With Full HTML Reporting:**
```bash
./run-shadow-tests.sh report
```

**Validate Setup:**
```bash
./run-shadow-tests.sh validate
```

## 🧪 Test Coverage

### AWS Provider Tests
- **Authentication Testing**: Validate AWS profile authentication across environments
- **Environment Switching**: Test switching between AWS environments
- **Capability Testing**: Verify AWS service capabilities (S3, EC2, RDS, etc.)
- **Command Execution**: Execute AWS CLI commands through the interface
- **Quick Commands**: Test pre-configured AWS quick command buttons
- **Error Handling**: Validate proper error responses and logging

### GCP Provider Tests
- **Authentication Testing**: Validate GCP service account and OAuth authentication
- **Project Switching**: Test switching between GCP projects
- **Capability Testing**: Verify GCP service capabilities (Compute, Storage, etc.)
- **Command Execution**: Execute gcloud commands through the interface
- **Quick Commands**: Test pre-configured GCP quick command buttons
- **Service Integration**: Test GCP-specific service interactions

### Kubernetes Provider Tests
- **Cluster Connectivity**: Validate kubectl cluster connections
- **Context Management**: Test switching between Kubernetes contexts
- **Resource Commands**: Test kubectl commands for nodes, pods, services, etc.
- **Namespace Operations**: Validate namespace listing and switching
- **Command Execution**: Execute kubectl commands through the interface
- **Quick Commands**: Test pre-configured kubectl quick command buttons

## 🛠 Technical Architecture

### Page Object Model

The `AdminPage` class (`utils/admin-page.js`) provides a clean interface for interacting with the admin UI:

```javascript
const adminPage = new AdminPage(page);

// Navigate to sections
await adminPage.navigateToSection('providers');

// Test authentication
await adminPage.testAuthentication('aws');

// Execute commands
await adminPage.executeCommand('aws', 'aws s3 ls');

// Wait for results
const result = await adminPage.waitForCommandResult();
```

### Test Configuration

The shadow test configuration (`shadow-test.config.js`) includes:
- **Parallel Execution**: Tests run with 6 workers for maximum speed
- **Provider Isolation**: Each test gets its own browser context for safety
- **Extended Timeouts**: Longer timeouts for real API calls
- **Custom Base URL**: Points to APEX admin interface
- **Comprehensive Reporting**: JSON, HTML, and JUnit output formats

### Error Handling

Tests include comprehensive error handling for:
- Network connectivity issues
- Authentication failures
- Invalid command execution
- Provider configuration problems
- Timeout scenarios

## 📊 Reports and Logging

### Report Formats

1. **Console Output**: Real-time test progress with "WARP-DEMO" logging tags
2. **HTML Reports**: Visual test results at `shadow-reports/html/index.html`
3. **JSON Reports**: Machine-readable results at `shadow-reports/results.json`
4. **JUnit XML**: CI/CD integration at `shadow-reports/junit.xml`

### Log Analysis

Tests provide detailed logging for:
- Authentication attempts and results
- Command executions and outputs
- Error conditions and recovery
- Performance timing information
- Provider state changes

## 🔧 Configuration

### Environment Variables

Tests respect APEX's environment configuration:
- `AWS_PROFILE`: AWS authentication profile
- `GOOGLE_APPLICATION_CREDENTIALS`: GCP service account
- `KUBECONFIG`: Kubernetes configuration file

### Provider Configuration

Each provider test reads from APEX's configuration system:
- AWS environments from `config/aws/`
- GCP projects from `config/gcp/`
- Kubernetes contexts from `config/k8s/`

## 🚨 Troubleshooting

### Common Issues

**APEX Server Not Running:**
```bash
❌ Admin interface is not accessible. Make sure APEX is running:
   python3 apex.py --web
```

**Playwright Not Installed:**
```bash
❌ Playwright not found. Installing...
npm install @playwright/test
npx playwright install chromium
```

**Authentication Failures:**
- Verify AWS profile configuration: `aws configure list`
- Check GCP credentials: `gcloud auth list`
- Validate Kubernetes context: `kubectl config current-context`

**Test Timeouts:**
- Increase timeout in `shadow-test.config.js`
- Check network connectivity to cloud providers
- Verify APEX server response times

### Debug Mode

For detailed debugging, modify test files to include:
```javascript
// Enable verbose logging
console.log('WARP-DEMO: Detailed debug info');

// Take screenshots on failure
await page.screenshot({ path: 'debug-screenshot.png', fullPage: true });

// Log page content
const content = await page.content();
console.log('WARP-DEMO: Page content:', content);
```

## 🔄 Continuous Integration

### CI/CD Integration

The shadow testing framework supports CI/CD pipelines:

```yaml
# Example GitHub Actions integration
- name: Run Shadow Tests
  run: |
    python3 apex.py --web &
    sleep 5
    cd web/testing/shadow
    ./run-shadow-tests.sh report
    
- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: shadow-test-reports
    path: web/testing/shadow/shadow-reports/
```

### Test Scheduling

For regular provider validation:
```bash
# Daily provider health checks
0 8 * * * /path/to/apex/web/testing/shadow/run-shadow-tests.sh all

# Weekly comprehensive reporting
0 9 * * 1 /path/to/apex/web/testing/shadow/run-shadow-tests.sh report
```

## 📝 Best Practices

### Writing New Tests

1. **Use the AdminPage abstraction** for UI interactions
2. **Include comprehensive assertions** for expected outcomes
3. **Add proper error handling** for network and authentication issues
4. **Use descriptive test names** that explain the validation being performed
5. **Include "WARP-DEMO" tags** in all logging output
6. **Test both success and failure scenarios**

### Maintaining Tests

1. **Keep tests independent** - each test should set up its own state
2. **Use real provider responses** - avoid mocking cloud provider APIs
3. **Update selectors** when admin UI changes
4. **Review timeout values** based on provider response times
5. **Monitor test flakiness** and improve stability

### Performance Optimization

1. **Run tests sequentially** to avoid provider state conflicts
2. **Cache authentication** where possible
3. **Use focused test runs** for specific provider validation
4. **Implement proper cleanup** after each test suite

## 🎉 Success Metrics

The shadow testing framework validates:
- ✅ Real provider authentication works end-to-end
- ✅ All capabilities are properly exposed and functional
- ✅ Command execution produces expected results
- ✅ Error handling provides meaningful feedback
- ✅ UI interactions work across different browsers
- ✅ Performance remains acceptable under real load

This ensures APEX's provider integrations work reliably in production environments without relying on mock data or intermediate test pages.