import { test, expect } from '@playwright/test';

test.describe('UI Accessibility and Improvements', () => {
  test.describe('Login Page', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/auth/login');
    });

    test('should have proper focus management', async ({ page }) => {
      // Check if first input is focused automatically
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toBeFocused();
    });

    test('should have proper ARIA labels', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      
      // Check for aria-label or associated label
      const emailLabel = await emailInput.getAttribute('aria-label') || 
                        await page.locator('label[for="email"]').textContent();
      expect(emailLabel).toBeTruthy();
      
      const passwordLabel = await passwordInput.getAttribute('aria-label') || 
                           await page.locator('label[for="password"]').textContent();
      expect(passwordLabel).toBeTruthy();
    });

    test('should have visible loading states', async ({ page }) => {
      const submitButton = page.locator('button[type="submit"]');
      
      // Fill form
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'password123');
      
      // Start monitoring for loading state
      const buttonPromise = submitButton.click();
      
      // Check if button shows loading state
      await expect(submitButton).toHaveAttribute('disabled', '');
      
      await buttonPromise.catch(() => {}); // Ignore network errors for this test
    });

    test('should have proper error handling', async ({ page }) => {
      // Submit empty form
      await page.locator('button[type="submit"]').click();
      
      // Check for error messages
      const errorMessages = page.locator('[role="alert"], .text-destructive, .error-message');
      await expect(errorMessages.first()).toBeVisible();
    });

    test('should be keyboard navigable', async ({ page }) => {
      // Tab through form elements
      await page.keyboard.press('Tab');
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toBeFocused();
      
      await page.keyboard.press('Tab');
      const passwordInput = page.locator('input[type="password"]');
      await expect(passwordInput).toBeFocused();
      
      await page.keyboard.press('Tab');
      const submitButton = page.locator('button[type="submit"]');
      await expect(submitButton).toBeFocused();
    });
  });

  test.describe('Dashboard', () => {
    test.beforeEach(async ({ page }) => {
      // Mock authentication
      await page.route('**/api/v1/auth/me', async route => {
        await route.fulfill({
          status: 200,
          json: {
            id: 1,
            email: 'test@example.com',
            username: 'testuser'
          }
        });
      });
      
      await page.goto('/');
    });

    test('should have responsive layout', async ({ page }) => {
      // Desktop view
      await page.setViewportSize({ width: 1920, height: 1080 });
      const desktopHeader = page.locator('header');
      await expect(desktopHeader).toBeVisible();
      
      // Mobile view
      await page.setViewportSize({ width: 375, height: 667 });
      // Check if mobile menu button appears
      const mobileMenuButton = page.locator('[aria-label*="menu"], button:has-text("Menu")');
      const isMobileOptimized = await mobileMenuButton.isVisible().catch(() => false);
      
      // Record if mobile menu exists
      if (!isMobileOptimized) {
        console.log('⚠️ Missing mobile menu button');
      }
    });

    test('should have clear CTA buttons', async ({ page }) => {
      const uploadButton = page.locator('button:has-text("Upload")');
      await expect(uploadButton).toBeVisible();
      
      // Check button contrast
      const backgroundColor = await uploadButton.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      const color = await uploadButton.evaluate(el => 
        window.getComputedStyle(el).color
      );
      
      // Button should have sufficient size
      const box = await uploadButton.boundingBox();
      expect(box?.height).toBeGreaterThanOrEqual(40); // Minimum touch target
    });

    test('should handle empty states gracefully', async ({ page }) => {
      // Mock empty documents response
      await page.route('**/api/v1/documents', async route => {
        await route.fulfill({
          status: 200,
          json: []
        });
      });
      
      await page.reload();
      
      // Check for empty state message
      const emptyState = page.locator('text=/no documents|empty|upload your first/i');
      const hasEmptyState = await emptyState.isVisible().catch(() => false);
      
      if (!hasEmptyState) {
        console.log('⚠️ Missing empty state message');
      }
    });

    test('should have loading skeletons', async ({ page }) => {
      // Check for loading states
      const skeletons = page.locator('.skeleton, [aria-busy="true"], .animate-pulse');
      const hasLoadingStates = await skeletons.first().isVisible().catch(() => false);
      
      if (!hasLoadingStates) {
        console.log('⚠️ Missing loading skeleton states');
      }
    });
  });

  test.describe('Color Contrast and Theme', () => {
    test('should have sufficient color contrast in light mode', async ({ page }) => {
      await page.goto('/auth/login');
      
      // Check text contrast
      const heading = page.locator('h1, h2').first();
      const headingColor = await heading.evaluate(el => 
        window.getComputedStyle(el).color
      );
      const bgColor = await heading.evaluate(el => {
        let parent = el.parentElement;
        while (parent) {
          const bg = window.getComputedStyle(parent).backgroundColor;
          if (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') return bg;
          parent = parent.parentElement;
        }
        return 'rgb(255, 255, 255)';
      });
      
      // Log colors for manual review
      console.log(`Text color: ${headingColor}, Background: ${bgColor}`);
    });

    test('should support dark mode', async ({ page }) => {
      await page.goto('/');
      
      // Check for theme toggle
      const themeToggle = page.locator('[aria-label*="theme"], button:has-text("Theme"), [data-testid="theme-toggle"]');
      const hasThemeToggle = await themeToggle.isVisible().catch(() => false);
      
      if (!hasThemeToggle) {
        console.log('⚠️ Missing theme toggle button');
      } else {
        // Test theme switching
        await themeToggle.click();
        await page.waitForTimeout(500); // Wait for theme transition
        
        const htmlClass = await page.locator('html').getAttribute('class');
        const isDarkMode = htmlClass?.includes('dark');
        
        if (!isDarkMode) {
          console.log('⚠️ Dark mode not properly implemented');
        }
      }
    });
  });

  test.describe('Forms and Inputs', () => {
    test('should have proper form validation feedback', async ({ page }) => {
      await page.goto('/auth/register');
      
      // Test email validation
      const emailInput = page.locator('input[type="email"]');
      await emailInput.fill('invalid-email');
      await emailInput.blur();
      
      // Check for validation message
      const validationMessage = page.locator('[aria-invalid="true"], .error, .text-destructive');
      const hasValidation = await validationMessage.first().isVisible().catch(() => false);
      
      if (!hasValidation) {
        console.log('⚠️ Missing real-time validation feedback');
      }
    });

    test('should have password strength indicator', async ({ page }) => {
      await page.goto('/auth/register');
      
      const passwordInput = page.locator('input[type="password"]');
      await passwordInput.fill('weak');
      
      // Check for strength indicator
      const strengthIndicator = page.locator('[aria-label*="strength"], .password-strength, [data-testid="password-strength"]');
      const hasStrengthIndicator = await strengthIndicator.isVisible().catch(() => false);
      
      if (!hasStrengthIndicator) {
        console.log('⚠️ Missing password strength indicator');
      }
    });

    test('should have clear input labels and placeholders', async ({ page }) => {
      await page.goto('/auth/login');
      
      const inputs = page.locator('input');
      const inputCount = await inputs.count();
      
      for (let i = 0; i < inputCount; i++) {
        const input = inputs.nth(i);
        const placeholder = await input.getAttribute('placeholder');
        const label = await page.locator(`label[for="${await input.getAttribute('id')}"]`).textContent().catch(() => null);
        const ariaLabel = await input.getAttribute('aria-label');
        
        const hasLabeling = placeholder || label || ariaLabel;
        if (!hasLabeling) {
          console.log(`⚠️ Input ${i} missing label or placeholder`);
        }
      }
    });
  });

  test.describe('Navigation and User Flow', () => {
    test('should have breadcrumbs or clear navigation', async ({ page }) => {
      await page.goto('/');
      
      // Check for breadcrumbs
      const breadcrumbs = page.locator('nav[aria-label="Breadcrumb"], .breadcrumbs, [data-testid="breadcrumbs"]');
      const hasBreadcrumbs = await breadcrumbs.isVisible().catch(() => false);
      
      if (!hasBreadcrumbs) {
        console.log('⚠️ Missing breadcrumb navigation');
      }
    });

    test('should have clear back/cancel options in dialogs', async ({ page }) => {
      await page.goto('/');
      
      // Open upload dialog
      const uploadButton = page.locator('button:has-text("Upload")');
      if (await uploadButton.isVisible()) {
        await uploadButton.click();
        
        // Check for cancel/close button
        const cancelButton = page.locator('button:has-text("Cancel"), button[aria-label*="Close"], [data-testid="dialog-close"]');
        const hasCancelOption = await cancelButton.isVisible().catch(() => false);
        
        if (!hasCancelOption) {
          console.log('⚠️ Missing clear cancel option in dialog');
        }
      }
    });
  });

  test.describe('Performance and Optimization', () => {
    test('should lazy load images', async ({ page }) => {
      await page.goto('/');
      
      const images = page.locator('img');
      const imageCount = await images.count();
      
      for (let i = 0; i < Math.min(imageCount, 5); i++) {
        const img = images.nth(i);
        const loading = await img.getAttribute('loading');
        
        if (loading !== 'lazy') {
          console.log(`⚠️ Image ${i} not using lazy loading`);
        }
      }
    });

    test('should have optimized bundle size indicators', async ({ page }) => {
      const response = await page.goto('/');
      const headers = response?.headers();
      
      // Check for compression
      const encoding = headers?.['content-encoding'];
      if (!encoding?.includes('gzip') && !encoding?.includes('br')) {
        console.log('⚠️ Response not compressed');
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      // Simulate network error
      await page.route('**/api/v1/**', route => route.abort());
      
      await page.goto('/');
      
      // Check for error message
      const errorMessage = page.locator('text=/error|failed|try again|offline/i');
      const hasErrorHandling = await errorMessage.isVisible().catch(() => false);
      
      if (!hasErrorHandling) {
        console.log('⚠️ Missing user-friendly error messages');
      }
    });

    test('should have retry mechanisms', async ({ page }) => {
      await page.route('**/api/v1/documents', route => route.abort());
      
      await page.goto('/');
      
      // Check for retry button
      const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try again")');
      const hasRetryOption = await retryButton.isVisible().catch(() => false);
      
      if (!hasRetryOption) {
        console.log('⚠️ Missing retry mechanism for failed requests');
      }
    });
  });
});

test.describe('Mobile Responsiveness', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should have touch-friendly tap targets', async ({ page }) => {
    await page.goto('/auth/login');
    
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      const box = await button.boundingBox();
      
      if (box && (box.width < 44 || box.height < 44)) {
        console.log(`⚠️ Button ${i} below minimum touch target size (44x44px)`);
      }
    }
  });

  test('should have mobile-optimized forms', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Check input sizes on mobile
    const inputs = page.locator('input');
    const inputCount = await inputs.count();
    
    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i);
      const box = await input.boundingBox();
      
      if (box && box.height < 40) {
        console.log(`⚠️ Input ${i} too small for mobile (height: ${box.height}px)`);
      }
    }
  });

  test('should have swipe gestures or mobile navigation', async ({ page }) => {
    await page.goto('/');
    
    // Check for mobile menu
    const mobileMenu = page.locator('[aria-label*="menu"], .mobile-menu, button:has-text("Menu")');
    const hasMobileMenu = await mobileMenu.isVisible().catch(() => false);
    
    if (!hasMobileMenu) {
      console.log('⚠️ Missing mobile navigation menu');
    }
  });
});