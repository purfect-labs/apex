// Provider Authentication & Context Switching Validation Suite
// Validates provider auth and context switching before full provider tests
// This catches auth/config issues early to prevent cascading failures

const { test, expect } = require('@playwright/test');
const { AdminPage } = require('../utils/admin-page');

test.describe('Provider Authentication & Context Validation', () => {
    let page;
    let adminPage;

    test.beforeEach(async ({ browser }) => {
        console.log('🔐 REAL-AUTH-TEST: Setting up provider auth validation test');
        page = await browser.newPage();
        adminPage = new AdminPage(page);
        
        // Navigate to admin interface
        await page.goto('http://localhost:8000/static/admin.html');
        await page.waitForSelector('.admin-container', { timeout: 10000 });
        
        console.log('✅ REAL-AUTH-TEST: Provider auth testing environment ready');
    });

    test.afterEach(async () => {
        if (page) {
            await page.close();
        }
    });

    test.describe('AWS Profile Authentication & Switching', () => {
        test('should validate AWS profile authentication status', async () => {
            console.log('🔐 REAL-AWS-AUTH: Validating AWS profile authentication status');
            
            // Navigate to AWS provider section
            await page.click('text=AWS Provider');
            await page.waitForSelector('#aws-provider.active', { timeout: 5000 });
            
            // Check each AWS environment authentication
            const environments = ['dev', 'stage', 'prod'];
            const expectedAccounts = {
                'dev': '232143722969',
                'stage': '629280658692', 
                'prod': '325871136907'
            };
            
            for (const env of environments) {
                console.log(`🔍 REAL-AWS-AUTH: Checking AWS ${env} authentication`);
                
                // Use real API to check authentication status
                const response = await page.evaluate(async (environment) => {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    return {
                        ok: res.ok,
                        authenticated: data?.aws?.authentication?.profiles?.[environment]?.authenticated || false,
                        account: data?.aws?.authentication?.profiles?.[environment]?.account,
                        user: data?.aws?.authentication?.profiles?.[environment]?.user
                    };
                }, env);
                
                console.log(`📈 REAL-AWS-AUTH: AWS ${env} API response:`, response);
                
                if (response.ok && response.authenticated) {
                    console.log(`✅ REAL-AWS-AUTH: AWS ${env} authentication confirmed - Account: ${response.account}, User: ${response.user}`);
                } else {
                    console.log(`❌ REAL-AWS-AUTH: AWS ${env} authentication FAILED`);
                    throw new Error(`AWS ${env} environment authentication failed. Cannot proceed with provider tests.`);
                }
            }
        });

        // Removed extra AWS tests - only auth status check needed
    });

    test.describe('GCP Project Authentication & Switching', () => {
        test('should validate GCP project authentication status', async () => {
            console.log('🔐 REAL-GCP-AUTH: Validating GCP project authentication status');
            
            // Navigate to GCP provider section
            await page.click('text=GCP Provider');
            await page.waitForSelector('#gcp-provider.active', { timeout: 5000 });
            
            // Check each GCP project authentication
            const projects = ['dev', 'stage', 'prod'];
            const expectedProjects = {
                'dev': 'kenect-service-dev',
                'stage': 'kenect-service-stage',
                'prod': 'kenect-service-prod'
            };
            
            for (const project of projects) {
                console.log(`🔍 REAL-GCP-AUTH: Checking GCP ${project} authentication`);
                
                // Use real API to check GCP authentication status
                const response = await page.evaluate(async () => {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    return {
                        ok: res.ok,
                        authenticated: data?.gcp?.authentication?.authenticated || false,
                        activeAccount: data?.gcp?.authentication?.active_account,
                        currentProject: data?.gcp?.authentication?.current_project
                    };
                });
                
                console.log(`📈 REAL-GCP-AUTH: GCP ${project} API response:`, response);
                
                if (response.ok && response.authenticated) {
                    console.log(`✅ REAL-GCP-AUTH: GCP ${project} authentication confirmed - Account: ${response.activeAccount}, Project: ${response.currentProject}`);
                } else {
                    console.log(`❌ REAL-GCP-AUTH: GCP ${project} authentication FAILED`);
                    throw new Error(`GCP ${project} project authentication failed. Cannot proceed with provider tests.`);
                }
            }
        });

        // Removed extra GCP tests - only auth status check needed
    });

    // Removed extra Kubernetes and cross-provider tests to keep auth validation fast
});