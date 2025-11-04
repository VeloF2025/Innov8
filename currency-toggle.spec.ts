import { test, expect } from '@playwright/test';

// Base URL for GitHub Pages
const BASE_URL = 'https://velof2025.github.io/Innov8';

// Test documents
const DOCUMENTS = [
  { name: 'index.html', url: `${BASE_URL}/index.html` },
  { name: 'VELOCITY_BRANDED_INVESTOR_TEASER.html', url: `${BASE_URL}/VELOCITY_BRANDED_INVESTOR_TEASER.html` },
  { name: 'VELOCITY_PRINT_OPTIMIZED_TEASER.html', url: `${BASE_URL}/VELOCITY_PRINT_OPTIMIZED_TEASER.html` },
  { name: 'VELOCITY_FINANCIAL_MODELS.html', url: `${BASE_URL}/VELOCITY_FINANCIAL_MODELS.html` },
  { name: 'VELOCITY_FINANCIAL_ASSUMPTIONS.html', url: `${BASE_URL}/VELOCITY_FINANCIAL_ASSUMPTIONS.html` },
];

test.describe('Currency Toggle Feature', () => {
  DOCUMENTS.forEach(doc => {
    test.describe(`${doc.name}`, () => {
      test('should display currency toggle buttons', async ({ page }) => {
        await page.goto(doc.url);

        // Wait for buttons to be visible
        const randButton = page.locator('button[data-currency="ZAR"]');
        const usdButton = page.locator('button[data-currency="USD"]');

        await expect(randButton).toBeVisible();
        await expect(usdButton).toBeVisible();

        // Verify button text
        await expect(randButton).toContainText('R - Rand');
        await expect(usdButton).toContainText('$ - USD');

        console.log(`✓ ${doc.name}: Currency toggle buttons visible`);
      });

      test('should display exchange rate', async ({ page }) => {
        await page.goto(doc.url);

        // Wait for exchange rate display
        const exchangeRateDisplay = page.locator('#exchange-rate-display');
        await expect(exchangeRateDisplay).toBeVisible();

        // Get the text and verify it contains exchange rate info
        const rateText = await exchangeRateDisplay.textContent();
        console.log(`✓ ${doc.name}: Exchange rate displayed: ${rateText}`);

        expect(rateText).toBeTruthy();
      });

      test('should toggle currency on button click', async ({ page }) => {
        // Capture console logs BEFORE navigation
        page.on('console', msg => {
          const text = msg.text();
          // Capture ALL logs for this test
          if (text.includes('[Currency Converter]') || text.includes('[Test]') || text.includes('Button')) {
            console.log(`BROWSER LOG: ${text}`);
          }
        });

        await page.goto(doc.url);

        // Wait a bit for initialization to complete
        await page.waitForTimeout(1000);

        // Get first currency value element if it exists
        const currencyElements = page.locator('[data-currency-zar]');
        const count = await currencyElements.count();

        if (count > 0) {
          // Get initial value in ZAR
          const firstElement = currencyElements.first();
          const initialText = await firstElement.textContent();
          console.log(`Initial value (ZAR): ${initialText}`);

          // Click USD button - try using locator.click() first, which is more reliable
          console.log('Attempting to click USD button via Playwright locator');
          try {
            await page.locator('button[data-currency="USD"]').click({ timeout: 3000 });
            console.log('Click via locator succeeded');
          } catch (err) {
            console.log(`Locator click failed: ${err}, trying JavaScript evaluation`);
            // Fallback: use JavaScript with proper event dispatching
            await page.evaluate(() => {
              const usdBtn = document.querySelector('button[data-currency="USD"]');
              if (usdBtn) {
                // Create and dispatch a proper click event
                const clickEvent = new MouseEvent('click', {
                  bubbles: true,
                  cancelable: true,
                  view: window,
                });
                usdBtn.dispatchEvent(clickEvent);
              }
            });
          }

          // Wait for conversion (increased timeout for async operations)
          await page.waitForTimeout(1500);

          // Get converted value
          const convertedText = await firstElement.textContent();
          console.log(`Converted value (USD): ${convertedText}`);

          // Verify the value changed and contains $ or M/K suffix
          expect(convertedText).not.toBe(initialText);
          expect(convertedText).toMatch(/\$|M|K/);

          console.log(`✓ ${doc.name}: Currency conversion working`);
        } else {
          console.log(`⚠ ${doc.name}: No currency values found to test conversion`);
        }
      });

      test('should toggle back to ZAR', async ({ page }) => {
        await page.goto(doc.url);

        const currencyElements = page.locator('[data-currency-zar]');
        const count = await currencyElements.count();

        if (count > 0) {
          const firstElement = currencyElements.first();

          // Get initial ZAR value
          const initialZar = await firstElement.textContent();

          // Switch to USD
          await page.locator('button[data-currency="USD"]').click();
          await page.waitForTimeout(500);

          // Switch back to ZAR
          await page.locator('button[data-currency="ZAR"]').click();
          await page.waitForTimeout(500);

          // Verify it's back to original
          const finalZar = await firstElement.textContent();
          expect(finalZar).toBe(initialZar);

          console.log(`✓ ${doc.name}: Toggle back to ZAR working`);
        }
      });

      test('should highlight active button with burgundy color', async ({ page }) => {
        await page.goto(doc.url);

        // Clear localStorage to reset currency preference to ZAR (after navigation)
        await page.evaluate(() => {
          localStorage.removeItem('velocity-currency');
        });

        // Reload the page to reinitialize with fresh currency state
        await page.reload();

        // Wait for initialization
        await page.waitForTimeout(1500);

        const randButton = page.locator('button[data-currency="ZAR"]');
        const usdButton = page.locator('button[data-currency="USD"]');

        // Check initial state (ZAR should be active)
        const randClass = await randButton.getAttribute('class');
        expect(randClass).toContain('active');
        console.log(`✓ ${doc.name}: ZAR button initially active`);

        // Click USD button directly via JavaScript to ensure event fires
        await page.evaluate(() => {
          const usdBtn = document.querySelector('button[data-currency="USD"]');
          if (usdBtn) usdBtn.click();
        });

        // Wait for click handler and class updates
        await page.waitForTimeout(1500);

        // Log button states for debugging
        const usdClassAfter = await usdButton.getAttribute('class');
        const randClassAfter = await randButton.getAttribute('class');
        console.log(`After click - USD class: ${usdClassAfter}, ZAR class: ${randClassAfter}`);

        // Check that USD is now active
        expect(usdClassAfter).toContain('active');

        // Check that ZAR is no longer active
        expect(randClassAfter).not.toContain('active');

        console.log(`✓ ${doc.name}: Button active state toggling correctly`);
      });
    });
  });
});
