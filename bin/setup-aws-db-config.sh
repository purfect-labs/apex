#!/usr/bin/env bash
set -euo pipefail
# --- portable sed -i flag setup ---
if [[ "$(uname)" == "Darwin" ]]; then
  SED_I=(-i '')
else
  SED_I=(-i)
fi

# --- escape values for sed replacement (escapes / and &) ---
sed_escape() {
  printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'
}

echo "🔍 Checking AWS Database configuration..."

# 1. If config file doesn't exist, copy from template
if [[ ! -f "$AWS_DB_CONFIG_FILE" ]]; then
    if [[ -f "$AWS_DB_CONFIG_FILE_TEMPLATE" ]]; then
        echo "📋 Creating database config from template..."
        cp "$AWS_DB_CONFIG_FILE_TEMPLATE" "$AWS_DB_CONFIG_FILE"
    else
        echo "❌ No database config or template found!"
        exit 1
    fi
fi

# 2. Check if REPLACE_ME is present in the config
if grep -q "REPLACE_ME" "$AWS_DB_CONFIG_FILE"; then
    echo "🔧 Database username needs configuration..."
    read -rp "📝 Enter your Database Username: " DB_USER
    
    echo "👤 Configuring database username: $DB_USER"
    DB_ESC=$(sed_escape "$DB_USER")
    
    # Replace REPLACE_ME with database username for all environments
    sed "${SED_I[@]}" "s|REPLACE_ME|${DB_ESC}|g" "$AWS_DB_CONFIG_FILE"
    
    echo "✅ Database configuration updated"
else
    echo "✅ Database configuration already set"
fi

# 3. Always validate the configuration exists and is readable
if [[ -f "$AWS_DB_CONFIG_FILE" ]]; then
    echo "📋 Current Database configuration:"
    cat "$AWS_DB_CONFIG_FILE"
    echo ""
    echo "✅ Database configuration validation complete"
else
    echo "❌ Database configuration file missing after setup"
    exit 1
fi
