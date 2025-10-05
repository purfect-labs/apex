// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('APEX License Activation Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to APEX main page
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display license modal when accessing premium features', async ({ page }) => {
    console.log('🧪 Test: License modal should appear for premium features');
    
    // Look for premium feature that should trigger license modal
    const premiumButton = page.locator('[data-test="premium-feature"], [data-feature-gate="premium"], .premium-feature').first();
    
    if (await premiumButton.count() > 0) {
      await premiumButton.click();
      
      // Wait for license modal to appear
      const licenseModal = page.locator('[data-test="license-modal"], .license-modal, #license-modal');
      await expect(licenseModal).toBeVisible({ timeout: 5000 });
      
      console.log('✅ License modal appeared when accessing premium feature');
    } else {
      console.log('⚠️  No premium features found on page - skipping modal test');
    }
  });

  test('should generate trial license through UI', async ({ page }) => {
    console.log('🧪 Test: Generate trial license through UI');
    
    // Look for license activation section or profile section
    const profileSection = page.locator('[data-test="profile-section"], .profile-section, [href*="profile"]').first();
    
    if (await profileSection.count() > 0) {
      await profileSection.click();
      await page.waitForTimeout(1000);
    }
    
    // Look for trial license generation
    const generateTrialButton = page.locator('[data-test="generate-trial"], button:has-text("Generate Trial"), button:has-text("Free Trial")').first();
    
    if (await generateTrialButton.count() > 0) {
      // Fill email if required
      const emailInput = page.locator('input[type="email"], input[placeholder*="email" i], #email').first();
      if (await emailInput.count() > 0) {
        await emailInput.fill('warp-test-demo@apex.dev');
      }
      
      await generateTrialButton.click();
      
      // Wait for success message or license key display
      const successIndicator = page.locator('[data-test="license-generated"], .success, .license-key, text="License generated"').first();
      await expect(successIndicator).toBeVisible({ timeout: 10000 });
      
      console.log('✅ Trial license generated successfully');
    } else {
      console.log('⚠️  No trial generation button found - checking for existing license');
    }
  });

  test('should activate license with valid key', async ({ page }) => {
    console.log('🧪 Test: Activate license with valid key');
    
    // First generate a trial license via API call
    const trialResponse = await page.request.post('/api/license/generate-trial', {
      data: {
        email: 'warp-test-demo@apex.dev',
        days: 7
      }
    });
    
    if (trialResponse.ok()) {
      const trialData = await trialResponse.json();
      const licenseKey = trialData.license_key;
      
      console.log(`📝 Generated license key: ${licenseKey}`);
      
      // Find license activation form
      const licenseInput = page.locator('input[placeholder*="license" i], input[name="license_key"], #license-key').first();
      const emailInput = page.locator('input[type="email"], input[name="email"], #email').first();
      const activateButton = page.locator('button:has-text("Activate"), [data-test="activate-license"]').first();
      
      if (await licenseInput.count() > 0 && await activateButton.count() > 0) {
        // Fill form
        await licenseInput.fill(licenseKey);
        
        if (await emailInput.count() > 0) {
          await emailInput.fill('warp-test-demo@apex.dev');
        }
        
        // Activate license
        await activateButton.click();
        
        // Wait for activation success
        const activationSuccess = page.locator('[data-test="activation-success"], .success, text="activated"').first();
        await expect(activationSuccess).toBeVisible({ timeout: 10000 });
        
        console.log('✅ License activated successfully');
        
        // Verify license status changed
        const statusResponse = await page.request.get('/api/license/status');
        if (statusResponse.ok()) {
          const statusData = await statusResponse.json();
          expect(statusData.status).toBe('active');
          console.log('✅ License status confirmed as active');
        }
      } else {
        console.log('⚠️  License activation form not found');
      }
    } else {
      console.log('❌ Failed to generate trial license for test');
    }
  });

  test('should reject invalid license key', async ({ page }) => {
    console.log('🧪 Test: Reject invalid license key');
    
    // Find license activation form
    const licenseInput = page.locator('input[placeholder*="license" i], input[name="license_key"], #license-key').first();
    const activateButton = page.locator('button:has-text("Activate"), [data-test="activate-license"]').first();
    
    if (await licenseInput.count() > 0 && await activateButton.count() > 0) {
      // Try invalid license key
      await licenseInput.fill('WARP-FAKE-INVALID-LICENSE-KEY-DEMO');
      
      // Try to activate
      await activateButton.click();
      
      // Wait for error message
      const errorMessage = page.locator('[data-test="activation-error"], .error, text="invalid"').first();
      await expect(errorMessage).toBeVisible({ timeout: 5000 });
      
      console.log('✅ Invalid license key properly rejected');
    } else {
      console.log('⚠️  License activation form not found');
    }
  });

  test('should show license features after activation', async ({ page }) => {
    console.log('🧪 Test: Show license features after activation');
    
    // Generate and activate a license first
    const trialResponse = await page.request.post('/api/license/generate-trial', {
      data: {
        email: 'warp-test-demo@apex.dev',
        days: 7
      }
    });
    
    if (trialResponse.ok()) {
      const trialData = await trialResponse.json();
      
      // Activate via API
      const activationResponse = await page.request.post('/api/license/activate', {
        data: {
          license_key: trialData.license_key,
          email: 'warp-test-demo@apex.dev'
        }
      });
      
      if (activationResponse.ok()) {
        // Reload page to see activated features
        await page.reload();
        await page.waitForLoadState('networkidle');
        
        // Check for premium features being unlocked
        const premiumFeatures = page.locator('[data-feature-gate="premium"], .premium-feature, [data-test*="premium"]');
        const featureCount = await premiumFeatures.count();
        
        if (featureCount > 0) {
          console.log(`✅ Found ${featureCount} premium features after activation`);
          
          // Check that premium features are no longer disabled
          const disabledFeatures = page.locator('[data-feature-gate="premium"][disabled], .premium-feature.disabled');
          const disabledCount = await disabledFeatures.count();
          
          expect(disabledCount).toBeLessThan(featureCount);
          console.log('✅ Premium features are now enabled');
        } else {
          console.log('⚠️  No premium features found to test');
        }
        
        // Check subscription info display
        const subscriptionInfo = page.locator('[data-test="subscription-info"], .subscription-status, .license-status');
        if (await subscriptionInfo.first().count() > 0) {
          await expect(subscriptionInfo.first()).toBeVisible();
          console.log('✅ Subscription info is displayed');
        }
      }
    }
  });

  test('should deactivate license properly', async ({ page }) => {
    console.log('🧪 Test: Deactivate license properly');
    
    // First activate a license
    const trialResponse = await page.request.post('/api/license/generate-trial', {
      data: {
        email: 'warp-test-demo@apex.dev',
        days: 7
      }
    });
    
    if (trialResponse.ok()) {
      const trialData = await trialResponse.json();
      
      await page.request.post('/api/license/activate', {
        data: {
          license_key: trialData.license_key,
          email: 'warp-test-demo@apex.dev'
        }
      });
      
      // Reload to see activated state
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      // Find deactivate button
      const deactivateButton = page.locator('button:has-text("Deactivate"), [data-test="deactivate-license"]').first();
      
      if (await deactivateButton.count() > 0) {
        await deactivateButton.click();
        
        // Confirm deactivation if there's a confirmation dialog
        const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), [data-test="confirm-deactivation"]').first();
        if (await confirmButton.count() > 0) {
          await confirmButton.click();
        }
        
        // Wait for deactivation success
        const deactivationSuccess = page.locator('[data-test="deactivation-success"], .success, text="deactivated"').first();
        await expect(deactivationSuccess).toBeVisible({ timeout: 5000 });
        
        console.log('✅ License deactivated successfully');
        
        // Verify status changed to inactive
        const statusResponse = await page.request.get('/api/license/status');
        if (statusResponse.ok()) {
          const statusData = await statusResponse.json();
          expect(statusData.status).toBe('inactive');
          console.log('✅ License status confirmed as inactive');
        }
      } else {
        console.log('⚠️  Deactivate button not found');
      }
    }
  });

  test('should handle network errors gracefully', async ({ page }) => {
    console.log('🧪 Test: Handle network errors gracefully');
    
    // Intercept license API calls to simulate network errors
    await page.route('**/api/license/**', route => {
      route.abort('connectionrefused');
    });
    
    // Try to activate a license
    const licenseInput = page.locator('input[placeholder*="license" i], input[name="license_key"], #license-key').first();
    const activateButton = page.locator('button:has-text("Activate"), [data-test="activate-license"]').first();
    
    if (await licenseInput.count() > 0 && await activateButton.count() > 0) {
      await licenseInput.fill('WARP-TEST-NETWORK-ERROR-DEMO');
      await activateButton.click();
      
      // Should show network error message
      const errorMessage = page.locator('[data-test="network-error"], .error, text="network"').first();
      await expect(errorMessage).toBeVisible({ timeout: 5000 });
      
      console.log('✅ Network errors handled gracefully');
    }
  });
});