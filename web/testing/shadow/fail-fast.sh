#!/bin/bash
# APEX Shadow Testing - Fail-Fast Runner
# Stops immediately on first test failure for debugging

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚨 APEX Shadow Tests - FAIL-FAST Mode"
echo "======================================"
echo ""
echo "🔍 This will run tests sequentially and stop on the FIRST failure"
echo "💡 Perfect for debugging issues without waiting for all tests"
echo ""

# Run the main test script with fail-fast flag
"$SCRIPT_DIR/run-shadow-tests.sh" fail-fast

exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    echo ""
    echo "🎉 ALL TESTS PASSED!"
    echo "✅ No failures detected in fail-fast mode"
else
    echo ""
    echo "❌ TEST FAILED - STOPPED ON FIRST FAILURE"
    echo "🔧 Fix the failing test and run again"
fi

exit $exit_code