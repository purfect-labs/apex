#!/usr/bin/env bash
# start-all-db-connections.sh - Start database connections for all environments

set -euo pipefail

echo "🚀 Starting all database connections..."

# Define environments and their ports ONCE
ENVIRONMENTS=(dev stage prod)
declare -A PORTS=(
    [dev]="5433"
    [stage]="5434" 
    [prod]="5435"
)

# Cleanup existing containers
cleanup() {
    echo "🧹 Cleaning up existing containers..."
    for env in "${ENVIRONMENTS[@]}"; do
        docker rm -f "apex-db-$env" 2>/dev/null || true
    done
}

# Start database connection for one environment
start_db_connection() {
    local env=$1
    local port=${PORTS[$env]}
    
    echo "🔌 Starting $env on port $port..."
    
    # Get database config
    DB_CONFIG=$(python3 -c "
import yaml
with open('$AWS_DB_CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
db = config['aws']['$env']
print(f\"{db['db_host']}|{db['db_name']}|{db['db_user']}|{db['db_port']}\")
")
    
    IFS='|' read -r DB_HOST DB_NAME DB_USER DB_PORT <<< "$DB_CONFIG"
    
    # Find bastion
    INSTANCE_ID=$(aws ec2 describe-instances \
        --profile "$env" \
        --region us-east-1 \
        --filters "Name=tag:Name,Values=bastion-*" "Name=instance-state-name,Values=running" \
        --query "Reservations[].Instances[0].InstanceId" \
        --output text 2>/dev/null)
    
    if [[ "$INSTANCE_ID" == "None" || -z "$INSTANCE_ID" ]]; then
        echo "   ❌ No bastion found for $env"
        return 1
    fi
    
    echo "   ✅ Found bastion: $INSTANCE_ID"
    
    # Start container
    docker run -d \
        --name "apex-db-$env" \
        -p "127.0.0.1:$port:$port" \
        -v "$HOME/.aws:/root/.aws" \
        -e AWS_REGION="us-east-1" \
        amazonlinux:latest \
        bash -c "
            yum install -y awscli nc socat >/dev/null 2>&1
            
            # Start SSM tunnel
            aws ssm start-session \
                --target $INSTANCE_ID \
                --document-name AWS-StartPortForwardingSessionToRemoteHost \
                --parameters host=$DB_HOST,portNumber=$DB_PORT,localPortNumber=5432 \
                --region us-east-1 \
                --profile $env &
            
            # Wait for tunnel
            for i in {1..30}; do
                nc -z 127.0.0.1 5432 2>/dev/null && break
                sleep 2
            done
            
            # Start port forwarder
            socat TCP-LISTEN:$port,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:5432 &
            
            echo '$env database ready on port $port'
            tail -f /dev/null
        "
    
    # Wait for port to be available
    for i in {1..15}; do
        if nc -z 127.0.0.1 "$port" 2>/dev/null; then
            echo "   ✅ $env ready: psql -h 127.0.0.1 -p $port -U $DB_USER $DB_NAME"
            return 0
        fi
        sleep 2
    done
    
    echo "   ❌ $env failed to start"
    docker logs "apex-db-$env" 2>/dev/null | tail -5
    return 1
}

# Main execution
cleanup

for env in "${ENVIRONMENTS[@]}"; do
    start_db_connection "$env"
done

echo ""
echo "🎉 Database connections ready!"
echo "   Dev:   localhost:5433"
echo "   Stage: localhost:5434" 
echo "   Prod:  localhost:5435"