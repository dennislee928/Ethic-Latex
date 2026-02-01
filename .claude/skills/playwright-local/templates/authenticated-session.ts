/**
 * Authenticated Session Scraping Template
 *
 * Demonstrates:
 * - Login automation
 * - Cookie persistence
 * - Session restoration
 * - Scraping protected content
 */

import { chromium } from 'playwright';
import fs from 'fs/promises';

const SESSION_FILE = 'session.json';

interface SessionCookies {
  cookies: Array<any>;
  timestamp: string;
}

async function saveSession(page: any) {
  const cookies = await page.context().cookies();
  const session: SessionCookies = {
    cookies,
    timestamp: new Date().toISOString(),
  };
  await fs.writeFile(SESSION_FILE, JSON.stringify(session, null, 2));
  console.log(`Session saved to ${SESSION_FILE}`);
}

async function loadSession(context: any): Promise<boolean> {
  try {
    const sessionData = await fs.readFile(SESSION_FILE, 'utf-8');
    const session: SessionCookies = JSON.parse(sessionData);

    await context.addCookies(session.cookies);
    console.log(`Session loaded from ${SESSION_FILE}`);
    return true;
  } catch {
    console.log('No existing session found');
    return false;
  }
}

async function login(page: any) {
  console.log('Performing login...');

  // Navigate to login page
  await page.goto('https://example.com/login');

  // Fill login form (customize for your site)
  await page.fill('input[name="email"]', process.env.EMAIL || '');
  await page.fill('input[name="password"]', process.env.PASSWORD || '');
  await page.click('button[type="submit"]');

  // Wait for redirect to dashboard (customize URL pattern)
  await page.waitForURL('**/dashboard', { timeout: 10000 });

  console.log('Login successful!');

  // Save session
  await saveSession(page);
}

async function scrapeProtectedContent(url: string, forceLogin = false) {
  const browser = await chromium.launch({ headless: false }); // Use headed for debugging
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Try to restore session
    const sessionLoaded = await loadSession(context);

    if (!sessionLoaded || forceLogin) {
      await login(page);
    } else {
      // Verify session is still valid by navigating to protected page
      await page.goto(url);

      // Check if redirected to login (session expired)
      if (page.url().includes('login')) {
        console.log('Session expired, logging in again...');
        await login(page);
        await page.goto(url);
      }
    }

    // Now on protected page, scrape data
    const data = {
      title: await page.title(),
      content: await page.locator('.protected-content').textContent(),
      timestamp: new Date().toISOString(),
    };

    console.log(JSON.stringify(data, null, 2));
    return data;
  } catch (error) {
    console.error('Scraping failed:', error);
    await page.screenshot({ path: 'auth-error.png' });
    throw error;
  } finally {
    await browser.close();
  }
}

// Run with: EMAIL=user@example.com PASSWORD=secret npx tsx authenticated-session.ts <url>
const url = process.argv[2] || 'https://example.com/protected-data';
const forceLogin = process.argv.includes('--force-login');

scrapeProtectedContent(url, forceLogin);
