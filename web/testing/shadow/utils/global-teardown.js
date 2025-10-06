// Global Teardown - Shadow Testing
// Cleanup and final reporting after all tests complete

const fs = require('fs').promises;
const path = require('path');

async function globalTeardown() {
    console.log('🧹 Shadow Testing Global Teardown Started');
    
    const reportsDir = path.join(__dirname, '..', 'shadow-reports');
    
    try {
        // Update test run metadata with completion time
        const metadataPath = path.join(reportsDir, 'test-run-metadata.json');
        
        try {
            const metadata = JSON.parse(await fs.readFile(metadataPath, 'utf8'));
            metadata.endTime = new Date().toISOString();
            metadata.duration = new Date() - new Date(metadata.startTime);
            
            await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
            
        } catch (error) {
            console.warn('⚠️  Could not update test run metadata:', error.message);
        }
        
        // Find the latest test run directory
        const latestRunDir = await findLatestTestRun(reportsDir);
        
        // Generate summary report
        const summary = {
            timestamp: new Date().toISOString(),
            reportsLocation: reportsDir,
            testType: 'shadow',
            latestRun: latestRunDir,
            structure: 'All test artifacts (videos, screenshots, traces, HTML reports) are in the same run directory'
        };
        
        await fs.writeFile(
            path.join(reportsDir, 'test-summary.json'),
            JSON.stringify(summary, null, 2)
        );
        
        // Log report locations
        console.log('📊 Shadow Test Reports Generated:');
        if (latestRunDir) {
            console.log(`   📁 Latest Run Directory: ${latestRunDir}`);
            
            // List what's actually in the run directory
            try {
                const files = await fs.readdir(latestRunDir, { withFileTypes: true });
                for (const file of files) {
                    const emoji = file.isDirectory() ? '📁' : '📄';
                    console.log(`     ${emoji} ${file.name}`);
                }
            } catch (error) {
                console.log(`     ⚠️  Could not list run directory contents`);
            }
        } else {
            console.log(`   ⚠️  No test run directory found`);
        }
        
        console.log('✅ Shadow Testing Global Teardown Completed');
        
    } catch (error) {
        console.error('❌ Shadow Testing Global Teardown Failed:', error);
        // Don't throw - teardown failures shouldn't fail the test run
    }
}

async function findLatestTestRun(reportsDir) {
    try {
        const testResultsDir = path.join(reportsDir, 'test-results');
        
        // Check if test-results directory exists
        try {
            await fs.access(testResultsDir);
        } catch {
            return null;
        }
        
        // Find all run directories (should start with shadow-test-run-)
        const entries = await fs.readdir(testResultsDir, { withFileTypes: true });
        const runDirs = entries
            .filter(entry => entry.isDirectory() && entry.name.startsWith('shadow-test-run-'))
            .map(entry => ({
                name: entry.name,
                path: path.join(testResultsDir, entry.name),
                timestamp: parseInt(entry.name.split('-').pop() || '0')
            }))
            .sort((a, b) => b.timestamp - a.timestamp); // Sort newest first
        
        return runDirs.length > 0 ? runDirs[0].path : null;
        
    } catch (error) {
        console.warn('⚠️  Could not find latest test run:', error.message);
        return null;
    }
}

module.exports = globalTeardown;
