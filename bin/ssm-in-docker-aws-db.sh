#!/usr/bin/env bash
# start-apex.sh - Start APEX with all database connections pre-established

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="$SCRIPT_DIR"

export APEX_BINS="$PROJECT_ROOT/bin"
export APEX_CONFIG_DIR="$PROJECT_ROOT/config"
export APEX_STATIC_CONFIG_DIR="$APEX_CONFIG_DIR/static"
export APEX_STATIC_CONFIG_TEMPLATE="$APEX_CONFIG_DIR/templates"

export AWS_DB_CONFIG_FILE_TEMPLATE="$APEX_STATIC_CONFIG_TEMPLATE/aws.db.config.template"
export AWS_SSO_CONFIG_FILE_TEMPLATE="$APEX_STATIC_CONFIG_TEMPLATE/aws.sso.config.template"

export AWS_SSO_CONFIG_FILE="$APEX_CONFIG_DIR/aws.sso.config"
export AWS_DB_CONFIG_FILE="$APEX_CONFIG_DIR/aws.db.config"

export AWS_CONFIG_DIR="$HOME/.aws"
export AWS_CONFIG_FILE="$AWS_CONFIG_DIR/config"
export BACKUP_FILE="$AWS_CONFIG_DIR/config.backup"

echo "🚀 APEX Command Center Startup"
echo "==============================="
echo ""

"$SCRIPT_DIR/bin/config-setup.sh"
"$APEX_BINS/start-all-db-connections.sh" &
DB_PID=$!

echo "🔄 Database connections starting in background (PID: $DB_PID)"
echo "🌐 APEX Web Interface will be available at: http://localhost:8000"
PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}" python3 -c "from web.main import run_server; run_server()"
