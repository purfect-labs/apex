// Shadow Testing Framework Configuration
// Tests provider layer capabilities through the admin UI
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: !process.env.FAIL_FAST, // Disable parallel when fail-fast is enabled
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : (process.env.FAIL_FAST ? 0 : 1),
  workers: process.env.CI ? 3 : (process.env.FAIL_FAST ? 1 : 6), // Single worker for fail-fast
  
  reporter: [
    ['html', { outputFolder: './shadow-reports/html' }],
    ['json', { outputFile: './shadow-reports/results.json' }],
    ['line'],
    ['junit', { outputFile: './shadow-reports/junit.xml' }]
  ],
  
  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1920, height: 1080 }, // Large viewport for admin interface
  },

  projects: [
    {
      name: 'shadow-testing-chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],

  webServer: {
    command: 'python3 apex.py --web',
    url: 'http://127.0.0.1:8000',
    reuseExistingServer: !process.env.CI,
    timeout: 60 * 1000, // 60 seconds for full APEX startup
    stdout: 'pipe',
    stderr: 'pipe',
  },

  // Shadow Testing specific settings
  expect: {
    timeout: 10000, // Provider operations can be slow
  },
  
  timeout: 120000, // 2 minutes for complex provider tests
});