// Shadow Testing - Admin Page Object Model
// Provides structured access to all provider testing capabilities

class AdminPage {
    constructor(page) {
        this.page = page;
        this.isInitialized = false; // Track if admin page is already loaded
        
        // Navigation selectors
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

        // AWS Provider selectors
        this.aws = {
            sections: {
                provider: '#aws-provider',
                commands: '#aws-commands'
            },
            statusCards: {
                dev: '#aws-dev-status',
                stage: '#aws-stage-status', 
                prod: '#aws-prod-status'
            },
            capabilities: {
                identity: 'button[onclick="testAWSCapability(\'identity\')"]',
                profiles: 'button[onclick="testAWSCapability(\'profiles\')"]',
                regions: 'button[onclick="testAWSCapability(\'regions\')"]',
                switchProfile: 'button[onclick="testAWSCapability(\'switch-profile\')"]'
            },
            commands: {
                envSelect: '#aws-env-select',
                input: '#aws-command-input',
                execute: 'button[onclick="executeAWSCommand()"]',
                output: '#aws-command-output',
                result: '#aws-command-result',
                quickButtons: {
                    identity: 'button[onclick="setAWSCommand(\'aws sts get-caller-identity\')"]',
                    ec2: 'button[onclick="setAWSCommand(\'aws ec2 describe-instances --max-items 5\')"]',
                    s3: 'button[onclick="setAWSCommand(\'aws s3 ls\')"]',
                    rds: 'button[onclick="setAWSCommand(\'aws rds describe-db-instances\')"]',
                    iam: 'button[onclick="setAWSCommand(\'aws iam get-user\')"]',
                    route53: 'button[onclick="setAWSCommand(\'aws route53 list-hosted-zones\')"]'
                }
            },
            providerOutput: {
                container: '#aws-provider-output',
                result: '#aws-provider-result'
            }
        };

        // GCP Provider selectors
        this.gcp = {
            sections: {
                provider: '#gcp-provider',
                commands: '#gcp-commands'
            },
            statusCards: {
                dev: '#gcp-dev-status',
                stage: '#gcp-stage-status',
                prod: '#gcp-prod-status'
            },
            capabilities: {
                authList: 'button[onclick="testGCPCapability(\'auth-list\')"]',
                projects: 'button[onclick="testGCPCapability(\'projects\')"]',
                switchProject: 'button[onclick="testGCPCapability(\'switch-project\')"]',
                config: 'button[onclick="testGCPCapability(\'config\')"]'
            },
            commands: {
                projectSelect: '#gcp-project-select',
                input: '#gcp-command-input',
                execute: 'button[onclick="executeGCPCommand()"]',
                output: '#gcp-command-output',
                result: '#gcp-command-result',
                quickButtons: {
                    authList: 'button[onclick="setGCPCommand(\'gcloud auth list\')"]',
                    projects: 'button[onclick="setGCPCommand(\'gcloud projects list\')"]',
                    vms: 'button[onclick="setGCPCommand(\'gcloud compute instances list --limit=5\')"]',
                    buckets: 'button[onclick="setGCPCommand(\'gcloud storage buckets list\')"]',
                    gke: 'button[onclick="setGCPCommand(\'gcloud container clusters list\')"]',
                    sql: 'button[onclick="setGCPCommand(\'gcloud sql instances list\')"]'
                }
            },
            providerOutput: {
                container: '#gcp-provider-output',
                result: '#gcp-provider-result'
            }
        };

        // Kubernetes Provider selectors
        this.k8s = {
            sections: {
                provider: '#k8s-provider',
                commands: '#kubectl-commands'
            },
            capabilities: {
                clusterInfo: 'button[onclick="testK8sCapability(\'cluster-info\')"]',
                contexts: 'button[onclick="testK8sCapability(\'contexts\')"]',
                namespaces: 'button[onclick="testK8sCapability(\'namespaces\')"]',
                nodes: 'button[onclick="testK8sCapability(\'nodes\')"]',
                pods: 'button[onclick="testK8sCapability(\'pods\')"]',
                services: 'button[onclick="testK8sCapability(\'services\')"]'
            },
            commands: {
                input: '#kubectl-command-input',
                execute: 'button[onclick="executeKubectlCommand()"]',
                output: '#kubectl-command-output',
                result: '#kubectl-command-result',
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
            },
            providerOutput: {
                container: '#k8s-provider-output',
                result: '#k8s-provider-result'
            }
        };

        // System status selectors
        this.system = {
            section: '#system-status',
            metrics: '#status-metrics',
            refreshButton: 'button[onclick="refreshStatus()"]'
        };

        // Logs selectors
        this.logs = {
            section: '#logs-viewer',
            container: '#live-logs',
            toggleButton: '#log-toggle'
        };
    }

    // Dynamic profile loading
    async loadAvailableProfiles() {
        if (this.profiles) return this.profiles; // Cache profiles
        
        const response = await this.page.evaluate(async () => {
            const resp = await fetch('/api/config/profiles');
            return await resp.json();
        });
        
        if (response.success) {
            this.profiles = {
                aws: response.aws_profiles,
                gcp: response.gcp_projects,
                aws_details: response.aws_profile_details,
                gcp_details: response.gcp_project_details
            };
        } else {
            throw new Error(`Failed to load profiles: ${response.error}`);
        }
        
        return this.profiles;
    }
    
    // Navigation methods
    async navigateToAdminPage() {
        // Skip navigation if already initialized and on admin page
        if (this.isInitialized) {
            try {
                const currentUrl = this.page.url();
                if (currentUrl.includes('/static/admin.html')) {
                    return; // Already on admin page, skip navigation
                }
            } catch {
                // If there's an error checking URL, proceed with navigation
            }
        }
        
        await this.page.goto('http://localhost:8000/static/admin.html');
        await this.page.waitForLoadState('networkidle');
        await this.waitForAdminInitialization();
        
        // Load dynamic profiles after page loads (only once)
        if (!this.isInitialized) {
            await this.loadAvailableProfiles();
            this.isInitialized = true;
        }
    }

    async waitForAdminInitialization() {
        // Wait for admin interface to fully initialize
        await this.page.waitForSelector('.admin-title');
        await this.page.waitForTimeout(2000); // Allow JS initialization
    }

    async navigateToSection(section) {
        const navSelector = this.navItems[section];
        if (!navSelector) {
            throw new Error(`Unknown section: ${section}`);
        }
        await this.page.click(navSelector);
        await this.page.waitForTimeout(1000); // Allow section transition
    }

    // AWS Provider testing methods
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

    async testAWSCapability(capability) {
        await this.navigateToSection('awsProvider');
        const buttonSelector = this.aws.capabilities[capability];
        
        await this.page.click(buttonSelector);
        await this.page.waitForSelector(this.aws.providerOutput.container, { state: 'visible' });
        await this.page.waitForTimeout(5000); // Allow API call to complete
        
        const resultText = await this.page.textContent(this.aws.providerOutput.result);
        return resultText;
    }

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

    // GCP Provider testing methods
    async testGCPAuthentication(project) {
        await this.navigateToSection('gcpProvider');
        const statusSelector = this.gcp.statusCards[project];
        
        // Click the status card to trigger auth test
        await this.page.click(statusSelector, { force: true });
        await this.page.waitForTimeout(3000);
        
        const statusText = await this.page.textContent(statusSelector);
        return statusText;
    }

    async testGCPCapability(capability) {
        await this.navigateToSection('gcpProvider');
        const buttonSelector = this.gcp.capabilities[capability];
        
        await this.page.click(buttonSelector);
        await this.page.waitForSelector(this.gcp.providerOutput.container, { state: 'visible' });
        await this.page.waitForTimeout(5000);
        
        const resultText = await this.page.textContent(this.gcp.providerOutput.result);
        return resultText;
    }

    async executeGCPCommand(command, project = 'dev') {
        await this.navigateToSection('gcpCommands');
        
        // Select project
        await this.page.selectOption(this.gcp.commands.projectSelect, project);
        
        // Enter command
        await this.page.fill(this.gcp.commands.input, command);
        
        // Execute
        await this.page.click(this.gcp.commands.execute);
        await this.page.waitForSelector(this.gcp.commands.output, { state: 'visible' });
        await this.page.waitForTimeout(10000); // GCP commands can be slow
        
        const resultText = await this.page.textContent(this.gcp.commands.result);
        return resultText;
    }

    // Kubernetes Provider testing methods
    async testK8sCapability(capability) {
        await this.navigateToSection('k8sProvider');
        const buttonSelector = this.k8s.capabilities[capability];
        
        await this.page.click(buttonSelector);
        await this.page.waitForSelector(this.k8s.providerOutput.container, { state: 'visible' });
        await this.page.waitForTimeout(5000);
        
        const resultText = await this.page.textContent(this.k8s.providerOutput.result);
        return resultText;
    }

    async executeKubectlCommand(command) {
        await this.navigateToSection('kubectlCommands');
        
        // Enter command
        await this.page.fill(this.k8s.commands.input, command);
        
        // Execute
        await this.page.click(this.k8s.commands.execute);
        await this.page.waitForSelector(this.k8s.commands.output, { state: 'visible' });
        await this.page.waitForTimeout(8000); // kubectl commands can be slow
        
        const resultText = await this.page.textContent(this.k8s.commands.result);
        return resultText;
    }

    // Utility methods
    async refreshSystemStatus() {
        await this.navigateToSection('systemStatus');
        await this.page.click(this.system.refreshButton);
        await this.page.waitForTimeout(3000);
    }

    async getLogEntries() {
        await this.navigateToSection('logsViewer');
        const logEntries = await this.page.locator('#live-logs .log-entry').allTextContents();
        return logEntries;
    }

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

    // Enhanced reporting and screenshot methods
    async captureScreenshot(testName, stepName = 'action') {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `shadow-test-${testName}-${stepName}-${timestamp}.png`;
        
        const screenshotPath = `shadow-reports/screenshots/${filename}`;
        await this.page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        
        return screenshotPath;
    }

    async captureTestEvidence(testName, capability, result) {
        const evidence = {
            testName,
            capability,
            timestamp: new Date().toISOString(),
            result: result.substring(0, 500), // Truncate for storage
            testType: 'shadow'
        };
        
        // Capture screenshot
        const screenshotPath = await this.captureScreenshot(testName, capability);
        evidence.screenshot = screenshotPath;
        
        // Log evidence
        console.log(`📸 Test Evidence Captured: ${JSON.stringify(evidence, null, 2)}`);
        
        return evidence;
    }

    async waitWithScreenshot(testName, waitDescription, waitFunction) {
        console.log(`⏳ ${waitDescription}`);
        
        try {
            await waitFunction();
            await this.captureScreenshot(testName, 'success');
        } catch (error) {
            await this.captureScreenshot(testName, 'failure');
            throw error;
        }
    }
}

module.exports = { AdminPage };
