// Playwright Configuration - Shadow Testing with Comprehensive Recording
// Records videos and screenshots for all tests (passes and failures)

const { defineConfig, devices } = require('@playwright/test');
const path = require('path');

const REPORTS_DIR = path.join(__dirname, 'shadow-reports');
const RUN_ID = `shadow-test-run-${Date.now()}`;
const RUN_DIR = path.join(REPORTS_DIR, 'test-results', RUN_ID);

module.exports = defineConfig({
  // Test directory
  testDir: './tests',
  
  // Timeout settings
  timeout: 120000, // 2 minutes per test
  expect: { timeout: 15000 }, // 15 seconds for assertions
  
  // Global setup/teardown
  globalSetup: require.resolve('./utils/global-setup.js'),
  globalTeardown: require.resolve('./utils/global-teardown.js'),
  
  // Test execution settings
  fullyParallel: true, // Run tests in parallel
  forbidOnly: !!process.env.CI, // Fail if test.only in CI
  retries: process.env.CI ? 2 : 1, // Retry failed tests
  workers: 6, // Use 6 workers for parallel execution
  
  // Reporter configuration
  reporter: [
    ['html', { 
      outputFolder: path.join(RUN_DIR, 'html-report'),
      open: 'never'
    }],
    ['junit', { 
      outputFile: path.join(RUN_DIR, 'junit-results.xml')
    }],
    ['json', { 
      outputFile: path.join(RUN_DIR, 'test-results.json')
    }],
    ['line']
  ],
  
  // Global test configuration
  use: {
    // Base URL for all tests
    baseURL: 'http://localhost:8000',
    
    // Browser settings
    headless: process.env.HEADLESS !== 'false',
    viewport: { width: 1920, height: 1080 },
    
    // Video recording - ALWAYS record (both pass and fail)
    video: {
      mode: 'on', // Always record videos
      size: { width: 1920, height: 1080 }
    },
    
    // Screenshot settings - take on both pass and fail
    screenshot: {
      mode: 'on', // Always take screenshots
      fullPage: true
    },
    
    // Trace collection - always collect
    trace: {
      mode: 'on', // Always collect traces
      screenshots: true,
      snapshots: true
    },
    
    // Network settings
    ignoreHTTPSErrors: true,
    
    // Action timeouts
    actionTimeout: 30000,
    navigationTimeout: 60000,
  },
  
  // Output directories - all in single run directory
  outputDir: RUN_DIR,
  
  // Project configurations
  projects: [
    {
      name: 'shadow-tests-chrome',
      use: {
        ...devices['Desktop Chrome'],
        // Override video settings to always record
        video: {
          mode: 'on', // Always record videos
          size: { width: 1920, height: 1080 }
        },
        // Override screenshot to capture on both pass and fail
        screenshot: {
          mode: 'on', // Always take screenshots
          fullPage: true
        }
      },
    },
    
    // Optional: Safari testing (uncomment if needed)
    // {
    //   name: 'shadow-tests-safari',
    //   use: {
    //     ...devices['Desktop Safari'],
    //     video: { mode: 'on' },
    //     screenshot: { mode: 'on', fullPage: true }
    //   },
    // },
    
    // Optional: Mobile testing (uncomment if needed)
    // {
    //   name: 'shadow-tests-mobile',
    //   use: {
    //     ...devices['iPhone 13'],
    //     video: { mode: 'on' },
    //     screenshot: { mode: 'on', fullPage: true }
    //   },
    // }
  ],
  
  // Web server configuration
  webServer: {
    command: './apex start',
    port: 8000,
    timeout: 60000,
    reuseExistingServer: !process.env.CI,
    cwd: path.join(__dirname, '../../..'), // Apex root directory
    stdout: 'ignore', // Suppress server stdout logs
    stderr: 'pipe',   // Keep stderr for actual errors
    env: {
      // Set environment for testing
      TESTING: 'true',
      LOG_LEVEL: 'ERROR', // Only show errors, not info logs
      // Add any other required environment variables
    }
  }
});