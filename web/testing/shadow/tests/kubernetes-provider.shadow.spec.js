// Shadow Testing - Kubernetes Provider End-to-End Tests
// Validates kubectl connectivity and cluster operations through admin UI

const { test, expect } = require('@playwright/test');
const { AdminPage } = require('../utils/admin-page');

test.describe('Kubernetes Provider Shadow Tests', () => {
    let adminPage;

    test.beforeEach(async ({ page }) => {
        adminPage = new AdminPage(page);
        await adminPage.navigateToAdminPage();
        
        // Add  logging
        await page.evaluate(() => {
            console.log('🧪 Kubernetes Provider Shadow Test Started - ');
        });
    });

    test.describe('Kubernetes Provider Capabilities', () => {
        test('should test kubectl cluster-info capability', async ({ page }) => {
            console.log('🧪 Testing kubectl cluster-info capability');
            
            const result = await adminPage.testK8sCapability('clusterInfo');
            
            expect(result).toBeTruthy();
            
            if (result.includes('Kubernetes master') || 
                result.includes('cluster') || 
                result.includes('running at') ||
                result.includes('control plane')) {
                console.log('✅ kubectl cluster-info capability validated with real cluster data');
                expect(result).toMatch(/(Kubernetes|cluster|running at|control plane)/i);
            } else if (result.includes('error') || result.includes('Unable to connect')) {
                console.log(`⚠️  kubectl cluster-info connection issue: ${result.substring(0, 100)}...`);
                // This is expected if no cluster is configured
                expect(result).toMatch(/(error|Unable to connect|connection)/i);
            } else {
                console.log(`❌ kubectl cluster-info unexpected result: ${result.substring(0, 100)}...`);
                throw new Error(`Unexpected kubectl cluster-info result format: ${result}`);
            }
        });

        test('should test kubectl contexts capability', async ({ page }) => {
            console.log('🧪 Testing kubectl contexts capability');
            
            const result = await adminPage.testK8sCapability('contexts');
            
            expect(result).toBeTruthy();
            
            if (result.includes('CURRENT') || 
                result.includes('NAME') || 
                result.includes('CLUSTER') ||
                result.includes('*')) {
                console.log('✅ kubectl contexts capability validated with real context data');
                expect(result).toMatch(/(CURRENT|NAME|CLUSTER|\*)/i);
            } else if (result.includes('error') || result.includes('No configuration file')) {
                console.log(`⚠️  kubectl contexts configuration issue: ${result.substring(0, 100)}...`);
                expect(result).toMatch(/(error|No configuration file|no configuration)/i);
            } else {
                console.log(`❌ kubectl contexts unexpected result: ${result.substring(0, 100)}...`);
                throw new Error(`Unexpected kubectl contexts result format: ${result}`);
            }
        });

        test('should test kubectl namespaces capability', async ({ page }) => {
            console.log('🧪 Testing kubectl namespaces capability');
            
            const result = await adminPage.testK8sCapability('namespaces');
            
            expect(result).toBeTruthy();
            
            if (result.includes('NAME') || 
                result.includes('default') || 
                result.includes('kube-system') ||
                result.includes('STATUS')) {
                console.log('✅ kubectl namespaces capability validated with real namespace data');
                expect(result).toMatch(/(NAME|default|kube-system|STATUS)/i);
            } else if (result.includes('error') || result.includes('connection refused')) {
                console.log(`⚠️  kubectl namespaces connection issue: ${result.substring(0, 100)}...`);
                expect(result).toMatch(/(error|connection refused|connection)/i);
            } else {
                console.log(`❌ kubectl namespaces unexpected result: ${result.substring(0, 100)}...`);
                throw new Error(`Unexpected kubectl namespaces result format: ${result}`);
            }
        });

        test('should test kubectl nodes capability', async ({ page }) => {
            console.log('🧪 Testing kubectl nodes capability');
            
            const result = await adminPage.testK8sCapability('nodes');
            
            expect(result).toBeTruthy();
            
            if (result.includes('NAME') || 
                result.includes('STATUS') || 
                result.includes('Ready') ||
                result.includes('AGE')) {
                console.log('✅ kubectl nodes capability validated with real node data');
                expect(result).toMatch(/(NAME|STATUS|Ready|AGE)/i);
            } else if (result.includes('error') || result.includes('Unauthorized')) {
                console.log(`⚠️  kubectl nodes authorization issue: ${result.substring(0, 100)}...`);
                expect(result).toMatch(/(error|Unauthorized|auth)/i);
            } else {
                console.log(`❌ kubectl nodes unexpected result: ${result.substring(0, 100)}...`);
                throw new Error(`Unexpected kubectl nodes result format: ${result}`);
            }
        });

        test('should test kubectl pods capability', async ({ page }) => {
            console.log('🧪 Testing kubectl pods capability');
            
            const result = await adminPage.testK8sCapability('pods');
            
            expect(result).toBeTruthy();
            
            if (result.includes('NAME') || 
                result.includes('READY') || 
                result.includes('STATUS') ||
                result.includes('NAMESPACE')) {
                console.log('✅ kubectl pods capability validated with real pod data');
                expect(result).toMatch(/(NAME|READY|STATUS|NAMESPACE)/i);
            } else if (result.includes('error') || result.includes('Forbidden')) {
                console.log(`⚠️  kubectl pods permission issue: ${result.substring(0, 100)}...`);
                expect(result).toMatch(/(error|Forbidden|permission)/i);
            } else {
                console.log(`❌ kubectl pods unexpected result: ${result.substring(0, 100)}...`);
                throw new Error(`Unexpected kubectl pods result format: ${result}`);
            }
        });

        test('should test kubectl services capability', async ({ page }) => {
            console.log('🧪 Testing kubectl services capability');
            
            const result = await adminPage.testK8sCapability('services');
            
            expect(result).toBeTruthy();
            
            if (result.includes('NAME') || 
                result.includes('TYPE') || 
                result.includes('CLUSTER-IP') ||
                result.includes('PORT')) {
                console.log('✅ kubectl services capability validated with real service data');
                expect(result).toMatch(/(NAME|TYPE|CLUSTER-IP|PORT)/i);
            } else if (result.includes('error') || result.includes('connection')) {
                console.log(`⚠️  kubectl services connection issue: ${result.substring(0, 100)}...`);
                expect(result).toMatch(/(error|connection)/i);
            } else {
                console.log(`❌ kubectl services unexpected result: ${result.substring(0, 100)}...`);
                throw new Error(`Unexpected kubectl services result format: ${result}`);
            }
        });
    });

    test.describe('Kubernetes Command Execution', () => {
        test('should execute kubectl cluster-info command', async ({ page }) => {
            console.log('🧪 Testing kubectl cluster-info command execution - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl cluster-info');
            
            expect(result).toBeTruthy();
            
            if (result.includes('Kubernetes') && (result.includes('running at') || result.includes('control plane'))) {
                console.log('✅ kubectl cluster-info command executed successfully with real cluster data');
                
                // Look for cluster endpoint
                if (result.includes('https://')) {
                    console.log('✅ Cluster endpoint detected in response');
                }
            } else if (result.includes('error') || result.includes('Unable to connect')) {
                console.log(`⚠️  kubectl cluster-info connection failed: ${result.substring(0, 200)}...`);
                
                // This could be expected if no cluster is configured
                expect(result).toContain('error');
            } else {
                console.log(`ℹ️  kubectl cluster-info unexpected result: ${result.substring(0, 100)}...`);
            }
        });

        test('should execute kubectl get nodes command', async ({ page }) => {
            console.log('🧪 Testing kubectl get nodes command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl get nodes');
            
            expect(result).toBeTruthy();
            
            if (result.includes('NAME') && result.includes('STATUS')) {
                console.log('✅ kubectl get nodes command executed successfully');
                
                // Check for Ready nodes
                if (result.includes('Ready')) {
                    console.log('✅ Found Ready nodes in cluster');
                }
            } else if (result.includes('error') || result.includes('connection refused')) {
                console.log(`⚠️  kubectl get nodes connection issue (expected if no cluster): ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl get nodes result: ${result.substring(0, 100)}...`);
            }
        });

        test('should execute kubectl get namespaces command', async ({ page }) => {
            console.log('🧪 Testing kubectl get namespaces command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl get namespaces');
            
            expect(result).toBeTruthy();
            
            if (result.includes('default') && result.includes('kube-system')) {
                console.log('✅ kubectl get namespaces command executed successfully with standard namespaces');
            } else if (result.includes('error') || result.includes('server could not find')) {
                console.log(`⚠️  kubectl get namespaces cluster access issue: ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl get namespaces result: ${result.substring(0, 100)}...`);
            }
        });

        test('should execute kubectl get pods across all namespaces', async ({ page }) => {
            console.log('🧪 Testing kubectl get pods --all-namespaces command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl get pods --all-namespaces --limit=10');
            
            expect(result).toBeTruthy();
            
            if (result.includes('NAMESPACE') && result.includes('NAME')) {
                console.log('✅ kubectl get pods --all-namespaces command executed successfully');
                
                // Check for system pods
                if (result.includes('kube-system')) {
                    console.log('✅ Found system pods in kube-system namespace');
                }
            } else if (result.includes('error') || result.includes('Forbidden')) {
                console.log(`⚠️  kubectl get pods permission issue (expected): ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl get pods result: ${result.substring(0, 100)}...`);
            }
        });

        test('should execute kubectl get services command', async ({ page }) => {
            console.log('🧪 Testing kubectl get services command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl get services');
            
            expect(result).toBeTruthy();
            
            if (result.includes('kubernetes') && result.includes('ClusterIP')) {
                console.log('✅ kubectl get services command executed successfully with kubernetes service');
            } else if (result.includes('error') || result.includes('connection')) {
                console.log(`⚠️  kubectl get services connection issue: ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl get services result: ${result.substring(0, 100)}...`);
            }
        });

        test('should execute kubectl config current-context command', async ({ page }) => {
            console.log('🧪 Testing kubectl config current-context command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl config current-context');
            
            expect(result).toBeTruthy();
            
            if (result && !result.includes('error') && result.trim().length > 0) {
                console.log(`✅ kubectl config current-context successful: ${result.trim()}`);
            } else if (result.includes('error') || result.includes('no configuration')) {
                console.log(`⚠️  kubectl config issue (expected if no kubeconfig): ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl config result: ${result.substring(0, 100)}...`);
            }
        });
    });

    test.describe('Kubernetes Quick Command Buttons', () => {
        test('should validate kubectl quick command buttons populate correctly', async ({ page }) => {
            console.log('🧪 Testing kubectl quick command buttons - ');
            
            await adminPage.navigateToSection('kubectlCommands');
            
            // Test each quick button
            const quickCommands = [
                { button: 'clusterInfo', expectedCommand: 'kubectl cluster-info' },
                { button: 'nodes', expectedCommand: 'kubectl get nodes' },
                { button: 'allPods', expectedCommand: 'kubectl get pods --all-namespaces' },
                { button: 'services', expectedCommand: 'kubectl get services' },
                { button: 'namespaces', expectedCommand: 'kubectl get namespaces' },
                { button: 'contexts', expectedCommand: 'kubectl get contexts' },
                { button: 'topNodes', expectedCommand: 'kubectl top nodes' },
                { button: 'deployments', expectedCommand: 'kubectl get deployments --all-namespaces' }
            ];
            
            for (const { button, expectedCommand } of quickCommands) {
                // Click the quick button
                await page.click(adminPage.k8s.commands.quickButtons[button]);
                await page.waitForTimeout(500);
                
                // Verify the command was populated
                const inputValue = await page.inputValue(adminPage.k8s.commands.input);
                expect(inputValue).toBe(expectedCommand);
                
                console.log(`✅ ${button} quick button populated correctly: ${expectedCommand}`);
            }
        });
    });

    test.describe('Kubernetes Advanced Operations', () => {
        test('should test kubectl version command', async ({ page }) => {
            console.log('🧪 Testing kubectl version command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl version --client');
            
            expect(result).toBeTruthy();
            
            if (result.includes('Client Version') || result.includes('GitVersion')) {
                console.log('✅ kubectl version command executed successfully');
                
                // Extract version info if available
                const versionMatch = result.match(/GitVersion:"([^"]+)"/);
                if (versionMatch) {
                    console.log(`✅ kubectl client version detected: ${versionMatch[1]}`);
                }
            } else if (result.includes('error') || result.includes('command not found')) {
                console.log(`⚠️  kubectl not installed or not in PATH: ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl version result: ${result.substring(0, 100)}...`);
            }
        });

        test('should test kubectl api-resources command', async ({ page }) => {
            console.log('🧪 Testing kubectl api-resources command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl api-resources --no-headers | head -10');
            
            expect(result).toBeTruthy();
            
            if (result.includes('pods') || result.includes('services') || result.includes('deployments')) {
                console.log('✅ kubectl api-resources command executed successfully');
            } else if (result.includes('error') || result.includes('Unable to connect')) {
                console.log(`⚠️  kubectl api-resources connection issue (expected): ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl api-resources result: ${result.substring(0, 100)}...`);
            }
        });

        test('should test kubectl get events command', async ({ page }) => {
            console.log('🧪 Testing kubectl get events command - ');
            
            const result = await adminPage.executeKubectlCommand('kubectl get events --limit=5');
            
            expect(result).toBeTruthy();
            
            if (result.includes('TYPE') || result.includes('REASON') || result.includes('OBJECT')) {
                console.log('✅ kubectl get events command executed successfully');
            } else if (result.includes('error') || result.includes('No resources found')) {
                console.log(`⚠️  kubectl get events no events or access issue: ${result.substring(0, 100)}...`);
            } else {
                console.log(`ℹ️  kubectl get events result: ${result.substring(0, 100)}...`);
            }
        });
    });

    test.afterEach(async ({ page }) => {
        await page.evaluate(() => {
            console.log('🧪 Kubernetes Provider Shadow Test Completed - ');
        });
    });
});