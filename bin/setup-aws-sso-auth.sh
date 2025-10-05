#!/usr/bin/env bash
set -euo pipefail

VALID_ROLES=(
  "attribute_frontend_members"
  "DevXAdmin"
  "attribute_devops"
  "attribute_backend_members"
  "attribute_teamlead_members"
)

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

# Method 1: Ensure SSO config exists and is properly configured
ensure_sso_config() {
echo "🔍 Checking AWS SSO configuration..."
echo "DEBUG: AWS_SSO_CONFIG_FILE_TEMPLATE=$AWS_SSO_CONFIG_FILE_TEMPLATE"
echo "DEBUG: AWS_SSO_CONFIG_FILE=$AWS_SSO_CONFIG_FILE"
    
    # 1. If config file doesn't exist, copy from template
    if [[ ! -f "$AWS_SSO_CONFIG_FILE" ]]; then
        if [[ -f "$AWS_SSO_CONFIG_FILE_TEMPLATE" ]]; then
            echo "📋 Creating SSO config from template..."
            cp "$AWS_SSO_CONFIG_FILE_TEMPLATE" "$AWS_SSO_CONFIG_FILE"
        else
            echo "❌ No SSO config or template found!"
            exit 1
        fi
    fi
    
    # 2. Check if REPLACE_ME is present in the AWS config
    if grep -q "REPLACE_ME" "$AWS_SSO_CONFIG_FILE"; then
        echo "🔧 AWS SSO role needs configuration..."
        echo "🔑 Select AWS SSO Role:"
        select USER_ROLE in "${VALID_ROLES[@]}"; do
            [[ -n "${USER_ROLE:-}" ]] && break
            echo "❌ Invalid selection, try again."
        done
        
        echo "📝 Configuring AWS SSO role: $USER_ROLE"
        ROLE_ESC=$(sed_escape "$USER_ROLE")
        
        # Replace REPLACE_ME with selected role in all profiles
        sed "${SED_I[@]}" "s|REPLACE_ME|${ROLE_ESC}|g" "$AWS_SSO_CONFIG_FILE"
        
        echo "✅ AWS SSO configuration updated"
    else
        echo "✅ AWS SSO configuration already set"
    fi
    
    echo "📋 Current AWS SSO configuration:"
    cat "$AWS_SSO_CONFIG_FILE"
    echo ""
}

# Method 2: Copy project config to ~/.aws/config
copy_to_aws_config() {
    mkdir -p "$AWS_CONFIG_DIR"
    
    # Check if current config matches project config
    if [[ -f "$AWS_CONFIG_FILE" ]] && diff -q "$AWS_CONFIG_FILE" "$AWS_SSO_CONFIG_FILE" >/dev/null; then
        echo "✅ ~/.aws/config is already identical to project config. No override needed."
    else
        echo "🛡️  Your ~/.aws/config is different from the project config"
        
        # Auto-confirm if running in non-interactive mode (from UI)
        if [[ "${APEX_NON_INTERACTIVE:-}" == "true" ]]; then
            CONFIRM="y"
        else
            read -rp "❓ Override ~/.aws/config with project config? (y/n): " CONFIRM
        fi

        if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
            if [[ -f "$AWS_CONFIG_FILE" ]]; then
                echo "📦 Backing up current config to: $BACKUP_FILE"
                cp "$AWS_CONFIG_FILE" "$BACKUP_FILE"
            fi

            echo "📁 Overriding ~/.aws/config with project config"
            cp "$AWS_SSO_CONFIG_FILE" "$AWS_CONFIG_FILE"
        else
            echo "❌ Aborted. Not overriding ~/.aws/config"
            exit 1
        fi
    fi
}

# Method 3: Validate all 3 profiles work
validate_all_profiles() {
    PROFILES=("dev" "stage" "prod")
    SSO_SESSION_VALID=false

    echo "🔎 Checking AWS SSO session status..."

    # Check if any profile is already authenticated
    for profile in "${PROFILES[@]}"; do
        if aws sts get-caller-identity --profile "$profile" >/dev/null 2>&1; then
            echo "✅ Profile '$profile' already authenticated"
            SSO_SESSION_VALID=true
        else
            echo "❌ Profile '$profile' needs authentication"
        fi
    done

    # If no profiles are authenticated, do SSO login
    if [[ "$SSO_SESSION_VALID" == "false" ]]; then
        echo "🔄 Starting AWS SSO login (will authenticate all profiles)..."
        # Use any profile for SSO login since they share the same session
        aws sso login --profile "dev"
        echo "✅ AWS SSO login completed"
    else
        echo "ℹ️  At least one profile is already authenticated"
    fi

    # Verify all profiles after authentication
    echo ""
    echo "🔍 Verifying all AWS profiles:"
    ALL_AUTHENTICATED=true

    for profile in "${PROFILES[@]}"; do
        echo "  Checking profile: $profile"
        if aws sts get-caller-identity --profile "$profile" >/dev/null 2>&1; then
            IDENTITY=$(aws sts get-caller-identity --profile "$profile" --output json)
            ACCOUNT=$(echo "$IDENTITY" | jq -r '.Account')
            ARN=$(echo "$IDENTITY" | jq -r '.Arn')
            echo "    ✅ $profile: Account $ACCOUNT"
            echo "       ARN: $ARN"
        else
            echo "    ❌ $profile: Authentication failed"
            ALL_AUTHENTICATED=false
        fi
    done

    if [[ "$ALL_AUTHENTICATED" == "true" ]]; then
        echo ""
        echo "🎉 All AWS profiles authenticated successfully!"
        echo "🔧 You can now use any profile: dev, stage, or prod"
    else
        echo ""
        echo "⚠️  Some profiles failed authentication. Please try running again."
        exit 1
    fi
}

# Main execution - call all methods
ensure_sso_config
copy_to_aws_config  
validate_all_profiles
