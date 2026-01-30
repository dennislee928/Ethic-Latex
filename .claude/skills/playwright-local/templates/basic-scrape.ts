/**
 * Basic Playwright Page Scrape Template
 *
 * Simple example showing fundamental Playwright patterns:
 * - Browser launch
 * - Page navigation with network idle wait
 * - Content extraction
 * - Proper browser cleanup
 */

import { chromium } from 'playwright';

async function scrapePage(url: string) {
  // Launch browser (headless by default)
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    // Navigate with network idle wait (good for SPAs)
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: 30000,
    });

    // Extract data
    const data = {
      title: await page.title(),
      url: page.url(),
      headings: await page.$$eval('h1, h2, h3', (elements) =>
        elements.map((el) => ({
          tag: el.tagName.toLowerCase(),
          text: el.textContent?.trim() || '',
        }))
      ),
      links: await page.$$eval('a[href]', (elements) =>
        elements.map((el) => ({
          text: el.textContent?.trim() || '',
          href: (el as HTMLAnchorElement).href,
        })).slice(0, 10) // Limit to first 10
      ),
      timestamp: new Date().toISOString(),
    };

    console.log(JSON.stringify(data, null, 2));
    return data;
  } catch (error) {
    console.error('Scraping failed:', error);
    throw error;
  } finally {
    // Always close browser to prevent zombie processes
    await browser.close();
  }
}

// Run with: npx tsx basic-scrape.ts <url>
const url = process.argv[2] || 'https://example.com';
scrapePage(url);
