/**
 * Screenshot Capture Template
 *
 * Full page screenshot patterns:
 * - Multiple formats (PNG, JPEG)
 * - Element screenshots
 * - Mobile viewport screenshots
 */

import { chromium } from 'playwright';
import path from 'path';

async function captureScreenshots(url: string, outputDir = './screenshots') {
  const browser = await chromium.launch({ headless: true });

  try {
    // Desktop screenshot
    console.log('Capturing desktop screenshot...');
    const desktopPage = await browser.newPage({
      viewport: { width: 1920, height: 1080 },
    });

    await desktopPage.goto(url, { waitUntil: 'networkidle' });

    await desktopPage.screenshot({
      path: path.join(outputDir, 'desktop-full.png'),
      fullPage: true,
      type: 'png',
    });

    // Mobile screenshot
    console.log('Capturing mobile screenshot...');
    const mobilePage = await browser.newPage({
      viewport: { width: 375, height: 667 }, // iPhone SE
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    });

    await mobilePage.goto(url, { waitUntil: 'networkidle' });

    await mobilePage.screenshot({
      path: path.join(outputDir, 'mobile-full.png'),
      fullPage: true,
      type: 'png',
    });

    // Element screenshot (header example)
    console.log('Capturing element screenshot...');
    const header = await desktopPage.locator('header').first();
    if (await header.count() > 0) {
      await header.screenshot({
        path: path.join(outputDir, 'header-only.png'),
      });
    }

    // Viewport screenshot (no full page scroll)
    console.log('Capturing viewport screenshot...');
    await desktopPage.screenshot({
      path: path.join(outputDir, 'desktop-viewport.png'),
      fullPage: false, // Only visible area
      type: 'jpeg',
      quality: 90,
    });

    console.log(`\nScreenshots saved to: ${outputDir}/`);

    await desktopPage.close();
    await mobilePage.close();
  } catch (error) {
    console.error('Screenshot capture failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

// Create output directory if needed
import fs from 'fs';
const outputDir = process.argv[3] || './screenshots';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Run with: npx tsx screenshot-capture.ts <url> [output-dir]
const url = process.argv[2] || 'https://example.com';
captureScreenshots(url, outputDir);
