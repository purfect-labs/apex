// AWS EC2 Component
class AWSEC2Component {
    constructor() {
        this.currentEnv = 'dev';
        this.render();
        this.bindEvents();
        this.listenForEnvironmentChanges();
    }

    render() {
        const container = document.getElementById('aws-ec2');
        if (!container) return;

        container.innerHTML = `
            <div class="command-category">
                <div class="category-title">🖥️ EC2 & Infrastructure</div>
                <div class="command-grid">
                    <button class="command-btn" data-action="list-instances">
                        <div class="command-icon">🖥️</div>
                        <div><strong>EC2 Instances</strong></div>
                        <div class="command-desc">List EC2 instances</div>
                    </button>
                    <button class="command-btn" data-action="list-security-groups">
                        <div class="command-icon">🔒</div>
                        <div><strong>Security Groups</strong></div>
                        <div class="command-desc">List security groups</div>
                    </button>
                    <button class="command-btn" data-action="list-vpcs">
                        <div class="command-icon">🌐</div>
                        <div><strong>VPCs</strong></div>
                        <div class="command-desc">List VPC networks</div>
                    </button>
                    <button class="command-btn" data-action="list-subnets">
                        <div class="command-icon">🔗</div>
                        <div><strong>Subnets</strong></div>
                        <div class="command-desc">List subnets</div>
                    </button>
                    <button class="command-btn" data-action="list-load-balancers">
                        <div class="command-icon">⚖️</div>
                        <div><strong>Load Balancers</strong></div>
                        <div class="command-desc">List ELB/ALB</div>
                    </button>
                    <button class="command-btn" data-action="list-eks-clusters">
                        <div class="command-icon">☸️</div>
                        <div><strong>EKS Clusters</strong></div>
                        <div class="command-desc">List EKS clusters</div>
                    </button>
                </div>
            </div>
        `;
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('#aws-ec2 .command-btn')) {
                const action = e.target.closest('.command-btn').dataset.action;
                this.handleAction(action);
            }
        });
    }

    listenForEnvironmentChanges() {
        window.addEventListener('environmentChanged', (e) => {
            this.currentEnv = e.detail.environment;
        });
    }

    handleAction(action) {
        const profile = `--profile ${this.currentEnv}`;
        
        switch (action) {
            case 'list-instances':
                this.listEC2Instances();
                break;
            case 'list-security-groups':
                if (window.executeCommand) {
                    window.executeCommand(`aws ec2 describe-security-groups ${profile} --output table`);
                }
                break;
            case 'list-vpcs':
                if (window.executeCommand) {
                    window.executeCommand(`aws ec2 describe-vpcs ${profile} --output table`);
                }
                break;
            case 'list-subnets':
                if (window.executeCommand) {
                    window.executeCommand(`aws ec2 describe-subnets ${profile} --output table`);
                }
                break;
            case 'list-load-balancers':
                if (window.executeCommand) {
                    window.executeCommand(`aws elbv2 describe-load-balancers ${profile} --output table`);
                }
                break;
            case 'list-eks-clusters':
                if (window.executeCommand) {
                    window.executeCommand(`aws eks list-clusters ${profile}`);
                }
                break;
        }
    }

    listEC2Instances() {
        if (window.addTerminalLine) {
            window.addTerminalLine('AWS', `🖥️ Fetching EC2 instances for ${this.currentEnv}...`, 'success');
        }

        if (window.executeCommand) {
            // Use a formatted query to get useful instance info
            const query = 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,PublicIpAddress,PrivateIpAddress,Tags[?Key==`Name`].Value|[0]]';
            window.executeCommand(`aws ec2 describe-instances --profile ${this.currentEnv} --query "${query}" --output table`);
        }
    }

    // Method to get instance details for a specific instance
    getInstanceDetails(instanceId) {
        if (window.executeCommand && instanceId) {
            window.executeCommand(`aws ec2 describe-instances --instance-ids ${instanceId} --profile ${this.currentEnv} --output json`);
        }
    }

    // Method to start/stop instances (would need confirmation UI)
    manageInstance(instanceId, action) {
        if (window.addTerminalLine) {
            window.addTerminalLine('AWS', `🔄 ${action}ing instance ${instanceId}...`, 'warning');
        }
        
        if (window.executeCommand && instanceId) {
            switch (action) {
                case 'start':
                    window.executeCommand(`aws ec2 start-instances --instance-ids ${instanceId} --profile ${this.currentEnv}`);
                    break;
                case 'stop':
                    window.executeCommand(`aws ec2 stop-instances --instance-ids ${instanceId} --profile ${this.currentEnv}`);
                    break;
                case 'reboot':
                    window.executeCommand(`aws ec2 reboot-instances --instance-ids ${instanceId} --profile ${this.currentEnv}`);
                    break;
            }
        }
    }
}

// Auto-initialize when loaded
window.AWSEC2Component = AWSEC2Component;