/**
 * Infinite Scroll Handler Template
 *
 * Handles dynamic content loading patterns:
 * - Scroll until no new content appears
 * - Deduplication with Set
 * - Configurable max items
 */

import { chromium } from 'playwright';

interface ScrollOptions {
  selector: string;
  maxItems?: number;
  maxScrolls?: number;
  scrollDelay?: number;
}

async function scrapeInfiniteScroll(
  page: any,
  options: ScrollOptions
) {
  const {
    selector,
    maxItems = Infinity,
    maxScrolls = 50,
    scrollDelay = 1500,
  } = options;

  const items = new Set<string>();
  let previousCount = 0;
  let noChangeCount = 0;
  let scrollCount = 0;

  console.log(`Starting infinite scroll for selector: ${selector}`);

  while (scrollCount < maxScrolls && items.size < maxItems) {
    // Get all visible elements
    const elements = await page.locator(selector).all();

    // Extract and deduplicate
    for (const el of elements) {
      const text = await el.textContent();
      if (text) {
        items.add(text.trim());
      }
    }

    console.log(`Items found: ${items.size} (scroll ${scrollCount + 1})`);

    // Check if we got new items
    if (items.size === previousCount) {
      noChangeCount++;
      if (noChangeCount >= 3) {
        console.log('No new items after 3 scrolls, stopping...');
        break;
      }
    } else {
      noChangeCount = 0;
    }

    previousCount = items.size;

    // Scroll to bottom
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(scrollDelay);

    scrollCount++;
  }

  return Array.from(items);
}

async function main(url: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    await page.goto(url, { waitUntil: 'networkidle' });

    // Customize selector for your target site
    const items = await scrapeInfiniteScroll(page, {
      selector: '.item', // Change to match your target
      maxItems: 100,
      maxScrolls: 20,
      scrollDelay: 2000,
    });

    console.log(`\nTotal items scraped: ${items.length}`);
    console.log(JSON.stringify(items, null, 2));

    return items;
  } catch (error) {
    console.error('Infinite scroll failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

// Run with: npx tsx infinite-scroll.ts <url>
const url = process.argv[2] || 'https://example.com/infinite-feed';
main(url);
