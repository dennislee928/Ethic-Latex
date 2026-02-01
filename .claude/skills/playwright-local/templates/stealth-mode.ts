/**
 * Playwright Stealth Mode Template
 *
 * Full anti-bot detection setup including:
 * - playwright-extra with stealth plugin
 * - WebDriver masking
 * - User agent rotation
 * - Human-like behavior
 */

import { chromium } from 'playwright-extra';
import stealth from 'puppeteer-extra-plugin-stealth';

// Apply stealth plugin
chromium.use(stealth());

async function stealthScrape(url: string) {
  // Launch with anti-detection args
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
    ],
  });

  // Randomize user agent (update these to latest Chrome versions)
  const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  ];

  const randomUA = userAgents[Math.floor(Math.random() * userAgents.length)];

  const context = await browser.newContext({
    userAgent: randomUA,
    viewport: {
      width: 1920 + Math.floor(Math.random() * 100), // Randomize slightly
      height: 1080 + Math.floor(Math.random() * 100)
    },
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });

  const page = await context.newPage();

  try {
    // Additional WebDriver masking
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });

      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
      });

      Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
      });
    });

    // Navigate with delay (human-like)
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: 60000
    });

    // Random delay before scraping (1-3 seconds)
    await page.waitForTimeout(1000 + Math.random() * 2000);

    // Extract data
    const data = {
      title: await page.title(),
      content: await page.textContent('body'),
      timestamp: new Date().toISOString(),
    };

    console.log(JSON.stringify(data, null, 2));
    return data;
  } catch (error) {
    console.error('Stealth scraping failed:', error);

    // Take screenshot on error for debugging
    await page.screenshot({ path: 'error-screenshot.png' });
    throw error;
  } finally {
    await browser.close();
  }
}

// Run with: npx tsx stealth-mode.ts <url>
const url = process.argv[2] || 'https://bot.sannysoft.com/';
stealthScrape(url);
