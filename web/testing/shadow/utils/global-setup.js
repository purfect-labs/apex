// Global Setup - Shadow Testing
// Prepares environment and ensures clean state before all tests

const fs = require('fs').promises;
const path = require('path');

async function globalSetup() {
    console.log('🚀 Shadow Testing Global Setup Started');
    
    const reportsDir = path.join(__dirname, '..', 'shadow-reports');
    
    try {
        // Ensure test-results directory exists
        const testResultsDir = path.join(reportsDir, 'test-results');
        
        try {
            await fs.access(testResultsDir);
        } catch {
            await fs.mkdir(testResultsDir, { recursive: true });
            console.log(`📁 Created directory: ${testResultsDir}`);
        }
        
        // Create test run metadata
        const metadata = {
            testRunId: `shadow-run-${Date.now()}`,
            startTime: new Date().toISOString(),
            environment: {
                node: process.version,
                platform: process.platform,
                pwd: process.cwd()
            },
            testType: 'shadow'
        };
        
        await fs.writeFile(
            path.join(reportsDir, 'test-run-metadata.json'),
            JSON.stringify(metadata, null, 2)
        );
        
        console.log('✅ Shadow Testing Global Setup Completed');
        
    } catch (error) {
        console.error('❌ Shadow Testing Global Setup Failed:', error);
        throw error;
    }
}

module.exports = globalSetup;