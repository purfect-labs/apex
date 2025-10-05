// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('UI Validation Tests - Element Accessibility', () => {
    let page;

    test.beforeEach(async ({ browser }) => {
        console.log('🧪 UI-VALIDATION: Setting up UI validation test');
        page = await browser.newPage();
        await page.goto('http://localhost:8000/static/admin.html');
        
        // Wait for page to load
        await page.waitForSelector('.admin-container', { timeout: 10000 });
        console.log('✅ UI-VALIDATION: Admin interface loaded successfully');
    });

    test.afterEach(async () => {
        if (page) {
            await page.close();
        }
    });

    test('should validate sidebar navigation elements exist', async () => {
        console.log('🔍 Checking sidebar navigation elements');
        
        // Check main sidebar structure
        await expect(page.locator('.sidebar')).toBeVisible();
        await expect(page.locator('.admin-title')).toBeVisible();
        
        // Check specific navigation items by exact text
        const navItems = [
            'AWS Provider',
            'GCP Provider', 
            'Kubernetes Provider',
            'AWS Commands',
            'GCP Commands',
            'kubectl Commands',
            'Live Status',
            'API Endpoints',
            'Live Logs'
        ];
        
        for (const itemText of navItems) {
            const navItem = page.locator(`.nav-item`).filter({ hasText: itemText });
            await expect(navItem).toBeVisible();
            console.log(`✅ Navigation item found: ${itemText}`);
        }
    });

    test('should validate AWS provider elements are accessible', async () => {
        console.log('🔍 Validating AWS provider UI elements');
        
        // Navigate to AWS provider section
        await page.click('text=AWS Provider');
        await page.waitForSelector('#aws-provider.active', { timeout: 5000 });
        
        // Check AWS environment status cards
        const awsEnvironments = ['dev', 'stage', 'prod'];
        for (const env of awsEnvironments) {
            const statusCardSelector = `#aws-${env}-status`;
            console.log(`🔍 Checking AWS ${env} status card: ${statusCardSelector}`);
            
            const statusCard = page.locator(statusCardSelector);
            await expect(statusCard).toBeVisible({ timeout: 5000 });
            
            // Check if the parent card is clickable
            const parentCard = statusCard.locator('xpath=..');
            await expect(parentCard).toBeVisible();
            console.log(`✅ AWS ${env} status card is accessible`);
        }
        
        // Check AWS capability test buttons
        const capabilityButtons = [
            'Test Identity (sts get-caller-identity)',
            'Test Profile List',
            'Test Region List', 
            'Test Profile Switching'
        ];
        
        for (const buttonText of capabilityButtons) {
            const button = page.locator('button').filter({ hasText: buttonText });
            await expect(button).toBeVisible();
            console.log(`✅ AWS capability button found: ${buttonText}`);
        }
        
        // Check output containers
        await expect(page.locator('#aws-provider-output')).toBeAttached();
        await expect(page.locator('#aws-provider-result')).toBeAttached();
    });

    test('should validate GCP provider elements are accessible', async () => {
        console.log('🔍 Validating GCP provider UI elements');
        
        // Navigate to GCP provider section  
        await page.click('text=GCP Provider');
        await page.waitForSelector('#gcp-provider.active', { timeout: 5000 });
        
        // Check GCP environment status cards
        const gcpEnvironments = ['dev', 'stage', 'prod'];
        for (const env of gcpEnvironments) {
            const statusCardSelector = `#gcp-${env}-status`;
            console.log(`🔍 Checking GCP ${env} status card: ${statusCardSelector}`);
            
            const statusCard = page.locator(statusCardSelector);
            await expect(statusCard).toBeVisible({ timeout: 5000 });
            console.log(`✅ GCP ${env} status card is accessible`);
        }
        
        // Check GCP capability test buttons
        const capabilityButtons = [
            'Test Auth List',
            'Test Project List',
            'Test Project Switching',
            'Test GCP Config'
        ];
        
        for (const buttonText of capabilityButtons) {
            const button = page.locator('button').filter({ hasText: buttonText });
            await expect(button).toBeVisible();
            console.log(`✅ GCP capability button found: ${buttonText}`);
        }
        
        // Check output containers
        await expect(page.locator('#gcp-provider-output')).toBeAttached();
        await expect(page.locator('#gcp-provider-result')).toBeAttached();
    });

    test('should validate Kubernetes provider elements are accessible', async () => {
        console.log('🔍 Validating Kubernetes provider UI elements');
        
        // Navigate to K8s provider section
        await page.click('text=Kubernetes Provider');
        await page.waitForSelector('#k8s-provider.active', { timeout: 5000 });
        
        // Check K8s capability test buttons (within the k8s-provider section)
        const capabilityButtons = [
            'Cluster Info',
            'List Contexts', 
            'List Namespaces',
            'List Nodes',
            'List Pods',
            'List Services'
        ];
        
        for (const buttonText of capabilityButtons) {
            const button = page.locator('#k8s-provider button').filter({ hasText: buttonText }).first();
            await expect(button).toBeVisible();
            console.log(`✅ K8s capability button found: ${buttonText}`);
        }
        
        // Check output containers
        await expect(page.locator('#k8s-provider-output')).toBeAttached();
        await expect(page.locator('#k8s-provider-result')).toBeAttached();
    });

    test('should validate command execution interfaces', async () => {
        console.log('🔍 Validating command execution interfaces');
        
        const commandSections = [
            { nav: 'text=AWS Commands', section: '#aws-commands', input: '#aws-command-input', output: '#aws-command-output' },
            { nav: 'text=GCP Commands', section: '#gcp-commands', input: '#gcp-command-input', output: '#gcp-command-output' },
            { nav: 'text=kubectl Commands', section: '#kubectl-commands', input: '#kubectl-command-input', output: '#kubectl-command-output' }
        ];
        
        for (const cmd of commandSections) {
            console.log(`🔍 Checking ${cmd.nav} interface`);
            
            // Navigate to command section
            await page.click(cmd.nav);
            await page.waitForSelector(`${cmd.section}.active`, { timeout: 5000 });
            
            // Check input field
            await expect(page.locator(cmd.input)).toBeVisible();
            await expect(page.locator(cmd.input)).toBeEditable();
            
            // Check output container exists
            await expect(page.locator(cmd.output)).toBeAttached();
            
            console.log(`✅ ${cmd.nav} interface is accessible`);
        }
    });

    test('should validate quick command buttons are functional', async () => {
        console.log('🔍 Validating quick command buttons');
        
        // Test AWS quick commands
        await page.click('text=AWS Commands');
        await page.waitForSelector('#aws-commands.active');
        
        const awsQuickCommands = [
            'Get Identity',
            'List EC2', 
            'List S3 Buckets',
            'List RDS',
            'Get IAM User',
            'List Route53'
        ];
        
        for (const cmd of awsQuickCommands) {
            const button = page.locator('button').filter({ hasText: cmd });
            await expect(button).toBeVisible();
            
            // Test button click populates input
            await button.click();
            const inputValue = await page.locator('#aws-command-input').inputValue();
            expect(inputValue.length).toBeGreaterThan(0);
            console.log(`✅ AWS quick command "${cmd}" populates input: ${inputValue}`);
        }
        
        // Test GCP quick commands
        await page.click('text=GCP Commands');
        await page.waitForSelector('#gcp-commands.active');
        
        const gcpQuickCommands = [
            'Auth List',
            'List Projects',
            'List VMs', 
            'List Buckets',
            'List GKE',
            'List CloudSQL'
        ];
        
        for (const cmd of gcpQuickCommands) {
            const button = page.locator('#gcp-commands button').filter({ hasText: cmd });
            await expect(button).toBeVisible();
            
            // Test button click populates input
            await button.click();
            const inputValue = await page.locator('#gcp-command-input').inputValue();
            expect(inputValue.length).toBeGreaterThan(0);
            console.log(`✅ GCP quick command "${cmd}" populates input: ${inputValue}`);
        }
        
        // Test Kubectl quick commands
        await page.click('text=kubectl Commands');
        await page.waitForSelector('#kubectl-commands.active');
        
        const kubectlQuickCommands = [
            'Cluster Info',
            'Get Nodes',
            'All Pods',
            'Get Services',
            'Get Namespaces', 
            'Get Contexts'
        ];
        
        for (const cmd of kubectlQuickCommands) {
            const button = page.locator('#kubectl-commands button').filter({ hasText: cmd });
            await expect(button).toBeVisible();
            
            // Test button click populates input
            await button.click();
            const inputValue = await page.locator('#kubectl-command-input').inputValue();
            expect(inputValue.length).toBeGreaterThan(0);
            console.log(`✅ Kubectl quick command "${cmd}" populates input: ${inputValue}`);
        }
    });

    test('should validate system status and logs sections', async () => {
        console.log('🔍 Validating system status and logs sections');
        
        // Test system status section
        await page.click('text=Live Status');
        await page.waitForSelector('#system-status.active');
        
        await expect(page.locator('#status-metrics')).toBeAttached();
        await expect(page.locator('button').filter({ hasText: 'Refresh Status' })).toBeVisible();
        
        // Test logs viewer section
        await page.click('text=Live Logs');
        await page.waitForSelector('#logs-viewer.active');
        
        await expect(page.locator('#live-logs')).toBeVisible();
        await expect(page.locator('#log-toggle')).toBeVisible();
        
        console.log('✅ System status and logs sections are accessible');
    });

    test('should validate all selectors used in AdminPage class', async () => {
        console.log('🔍 Validating all selectors used by AdminPage class');
        
        // Critical selectors that AdminPage relies on
        const criticalSelectors = [
            '.admin-container',
            '.sidebar',
            '.nav-item', 
            '#aws-provider',
            '#gcp-provider',
            '#k8s-provider',
            '#aws-dev-status',
            '#aws-stage-status', 
            '#aws-prod-status',
            '#gcp-dev-status',
            '#gcp-stage-status',
            '#gcp-prod-status',
            '#aws-provider-output',
            '#aws-provider-result',
            '#gcp-provider-output', 
            '#gcp-provider-result',
            '#k8s-provider-output',
            '#k8s-provider-result',
            '#aws-command-input',
            '#gcp-command-input',
            '#kubectl-command-input',
            '#aws-command-output',
            '#gcp-command-output', 
            '#kubectl-command-output',
            '#aws-command-result',
            '#gcp-command-result',
            '#kubectl-command-result'
        ];
        
        for (const selector of criticalSelectors) {
            const element = selector === '.nav-item' ? page.locator(selector).first() : page.locator(selector);
            await expect(element).toBeAttached({ timeout: 5000 });
            console.log(`✅ Critical selector is attached: ${selector}`);
        }
        
        console.log('🎉 All critical selectors validated successfully');
    });
});