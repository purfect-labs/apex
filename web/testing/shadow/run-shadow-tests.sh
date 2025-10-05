#!/bin/bash
# Shadow Testing Framework - Main Test Runner
# Executes comprehensive provider layer testing through admin UI

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"

echo "🧪 APEX Shadow Testing Framework"
echo "================================="
echo ""
echo "📁 Test Directory: $SCRIPT_DIR"
echo "📁 Project Root: $PROJECT_ROOT"
echo ""

# Ensure we're in the correct directory
cd "$SCRIPT_DIR"

# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found. Please install Node.js and npm first."
    exit 1
fi

if ! npx playwright --version &> /dev/null; then
    echo "❌ Playwright not found. Installing..."
    cd "$PROJECT_ROOT"
    npm install @playwright/test
    npx playwright install chromium
    cd "$SCRIPT_DIR"
fi

# Create shadow reports directory
mkdir -p shadow-reports

# Function to run UI validation tests first
run_ui_validation() {
    echo "🎯 Running UI Validation Tests First..."
    echo "📝 Validating all UI elements before API testing"
    
    npx playwright test "tests/ui-validation.shadow.spec.js" \
        --config=shadow-test.config.js \
        --reporter=line \
        --project=shadow-testing-chromium \
        --timeout=60000
    
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        echo "❌ UI Validation failed! Cannot proceed with API tests."
        echo "💡 Fix UI element accessibility issues first."
        return 1
    fi
    
    echo "✅ UI Validation passed - proceeding with provider auth validation"
    echo ""
    return 0
}

# Function to run provider authentication and context validation
run_provider_auth_validation() {
    echo "🔐 Running Provider Authentication & Context Validation..."
    echo "📝 Validating AWS profiles, GCP projects, kubectl configs before full tests"
    
    npx playwright test "tests/provider-auth-validation.shadow.spec.js" \
        --config=shadow-test.config.js \
        --reporter=line \
        --project=shadow-testing-chromium \
        --timeout=30000
    
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        echo "❌ Provider Authentication Validation failed! Check auth configs."
        echo "💡 Verify AWS profiles, GCP projects, and kubectl contexts are properly configured."
        return 1
    fi
    
    echo "✅ Provider Authentication Validation passed - proceeding with full provider tests"
    echo ""
    return 0
}

# Function to run individual provider tests
run_provider_tests() {
    local provider=$1
    local test_file="tests/${provider}-provider.shadow.spec.js"
    
    echo "🧪 Running ${provider} Provider Shadow Tests..."
    echo "📝 Test file: $test_file"
    
    if [[ ! -f "$test_file" ]]; then
        echo "❌ Test file not found: $test_file"
        return 1
    fi
    
    # Run the specific provider test with parallel workers
    npx playwright test "$test_file" \
        --config=shadow-test.config.js \
        --reporter=line \
        --project=shadow-testing-chromium \
        --workers=6 \
        --timeout=120000 || true
        
    echo "✅ ${provider} Provider tests completed"
    echo ""
}

# Function to run tests with fail-fast (stop on first failure)
run_fail_fast_tests() {
    echo "🚨 Running Shadow Tests with FAIL-FAST (stop on first failure)..."
    echo ""
    
    # Set fail-fast environment variable
    export FAIL_FAST=1
    
    # Run UI validation first
    if ! run_ui_validation; then
        echo "❌ UI Validation failed! Stopping execution."
        return 1
    fi
    
    # Run provider auth validation second
    if ! run_provider_auth_validation; then
        echo "❌ Provider Authentication failed! Stopping execution."
        return 1
    fi
    
    # Run tests sequentially with fail-fast - stop on first failure
    echo "🚨 Executing tests sequentially with FAIL-FAST mode..."
    echo "   - Single worker, no retries, stop on first failure"
    
    # Test AWS provider first
    echo "🔍 Testing AWS Provider (fail-fast)..."
    npx playwright test tests/aws-provider.shadow.spec.js \
        --config=shadow-test.config.js \
        --reporter=line \
        --project=shadow-testing-chromium \
        --workers=1 \
        --max-failures=1 \
        --timeout=120000
    
    local aws_exit=$?
    if [[ $aws_exit -ne 0 ]]; then
        echo "❌ AWS Provider test failed! Stopping execution (FAIL-FAST)."
        unset FAIL_FAST
        return 1
    fi
    
    # Test GCP provider second
    echo "🔍 Testing GCP Provider (fail-fast)..."
    npx playwright test tests/gcp-provider.shadow.spec.js \
        --config=shadow-test.config.js \
        --reporter=line \
        --project=shadow-testing-chromium \
        --workers=1 \
        --max-failures=1 \
        --timeout=120000
    
    local gcp_exit=$?
    if [[ $gcp_exit -ne 0 ]]; then
        echo "❌ GCP Provider test failed! Stopping execution (FAIL-FAST)."
        unset FAIL_FAST
        return 1
    fi
    
    # Test Kubernetes provider third
    echo "🔍 Testing Kubernetes Provider (fail-fast)..."
    npx playwright test tests/kubernetes-provider.shadow.spec.js \
        --config=shadow-test.config.js \
        --reporter=line \
        --project=shadow-testing-chromium \
        --workers=1 \
        --max-failures=1 \
        --timeout=120000
    
    local k8s_exit=$?
    if [[ $k8s_exit -ne 0 ]]; then
        echo "❌ Kubernetes Provider test failed! Stopping execution (FAIL-FAST)."
        unset FAIL_FAST
        return 1
    fi
    
    echo "🎉 All tests passed with FAIL-FAST mode!"
    unset FAIL_FAST
    return 0
}

# Function to run all shadow tests in parallel
run_all_tests() {
    echo "🚀 Running All Provider Shadow Tests in Parallel..."
    echo ""
    
    # Run UI validation first
    if ! run_ui_validation; then
        echo "❌ Cannot proceed with provider tests due to UI validation failure"
        return 1
    fi
    
    # Run provider auth validation second
    if ! run_provider_auth_validation; then
        echo "❌ Cannot proceed with full provider tests due to auth validation failure"
        return 1
    fi
    
    # Run all provider tests in parallel with 6 workers
    echo "🚀 Executing all provider tests with 6 parallel workers..."
    npx playwright test tests/aws-provider.shadow.spec.js tests/gcp-provider.shadow.spec.js tests/kubernetes-provider.shadow.spec.js \
        --config=shadow-test.config.js \
        --reporter=line \
        --project=shadow-testing-chromium \
        --workers=6 \
        --timeout=120000 || true
    
    echo "🎉 All Shadow Tests Completed!"
    echo ""
    echo "📈 Test Reports Available:"
    echo "  - HTML Report: shadow-reports/html/index.html"
    echo "  - JSON Report: shadow-reports/results.json"
    echo "  - JUnit Report: shadow-reports/junit.xml"
    echo ""
}

# Function to run tests with full reporting
run_with_full_reporting() {
    echo "📊 Running Shadow Tests with Full Reporting..."
    echo ""
    
    npx playwright test tests/ \
        --config=shadow-test.config.js \
        --reporter=html \
        --project=shadow-testing-chromium \
        --workers=6 \
        --timeout=120000
        
    echo "✅ Full reporting tests completed"
    echo ""
    echo "📊 Open HTML Report:"
    echo "  file://$SCRIPT_DIR/shadow-reports/html/index.html"
}

# Function to run specific provider test
run_specific_provider() {
    local provider=$1
    echo "🎯 Running Specific Provider Test: $provider"
    echo ""
    
    run_provider_tests "$provider"
}

# Function to validate admin interface accessibility
validate_admin_interface() {
    echo "🔍 Validating Admin Interface Accessibility..."
    echo ""
    
    # Try to access the admin interface
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/admin.html | grep -q "200"; then
        echo "✅ Admin interface is accessible at http://localhost:8000/static/admin.html"
    else
        echo "❌ Admin interface is not accessible. Make sure APEX is running:"
        echo "   python3 apex.py --web"
        echo ""
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  all                    Run all provider shadow tests in parallel (6 workers)"
    echo "  parallel               Run all tests in parallel (alias for 'all')"
    echo "  fail-fast              Run tests sequentially, stop on first failure (RECOMMENDED for debugging)"
    echo "  ui                     Run UI validation tests only"
    echo "  auth                   Run provider auth & context validation only"
    echo "  aws                    Run AWS provider tests only"
    echo "  gcp                    Run GCP provider tests only"
    echo "  kubernetes|k8s         Run Kubernetes provider tests only"
    echo "  report                 Run tests with full HTML reporting (parallel)"
    echo "  validate               Validate admin interface accessibility"
    echo "  help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run-shadow-tests.sh fail-fast   # RECOMMENDED: Stop on first failure (debugging)"
    echo "  ./run-shadow-tests.sh parallel    # Fast parallel execution"
    echo "  ./run-shadow-tests.sh all         # Same as parallel"
    echo "  ./run-shadow-tests.sh ui          # UI validation only"
    echo "  ./run-shadow-tests.sh auth        # Provider auth validation only"
    echo "  ./run-shadow-tests.sh aws         # AWS provider only"
    echo "  ./run-shadow-tests.sh report      # With HTML reports"
    echo "  ./run-shadow-tests.sh validate    # Check accessibility"
    echo ""
}

# Main execution logic
case "${1:-all}" in
    "all"|"parallel")
        validate_admin_interface && run_all_tests
        ;;
    "fail-fast")
        validate_admin_interface && run_fail_fast_tests
        ;;
    "ui")
        validate_admin_interface && run_ui_validation
        ;;
    "auth")
        validate_admin_interface && run_provider_auth_validation
        ;;
    "aws")
        validate_admin_interface && run_specific_provider "aws"
        ;;
    "gcp")
        validate_admin_interface && run_specific_provider "gcp"
        ;;
    "kubernetes"|"k8s")
        validate_admin_interface && run_specific_provider "kubernetes"
        ;;
    "report")
        validate_admin_interface && run_with_full_reporting
        ;;
    "validate")
        validate_admin_interface
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac

echo "🎯 Shadow Testing Framework Complete!"
echo ""
echo "💡 Tips:"
echo "  - Make sure APEX is running: python3 apex.py --web"
echo "  - Check reports in: $SCRIPT_DIR/shadow-reports/"
echo "  - View admin interface: http://localhost:8000/static/admin.html"