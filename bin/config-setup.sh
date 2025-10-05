#!/usr/bin/env bash
set -euo pipefail
echo "🚀 APEX Configuration Setup"
echo "=========================="
echo ""
$APEX_BINS/setup-aws-sso-auth.sh
$APEX_BINS/setup-aws-db-config.sh

