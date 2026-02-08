# Playwright Stealth Techniques

Complete guide to avoiding bot detection with Playwright.

## Detection Vectors

Sites detect automation through:

1. **navigator.webdriver** - Most common flag (true = automated)
2. **Missing plugins** - Real browsers have plugins array populated
3. **Chrome DevTools Protocol** - CDP detection via window.chrome
4. **WebGL fingerprinting** - Renderer/vendor strings
5. **Canvas fingerprinting** - Consistent pixel output
6. **Permissions** - Automated browsers have different permission APIs
7. **Consistent patterns** - Same viewport, same timing, same user agent
8. **Datacenter IPs** - Cloud/hosting IP ranges flagged

## Multi-Layer Defense

### Layer 1: playwright-extra + Stealth Plugin

```typescript
import { chromium } from 'playwright-extra';
import stealth from 'puppeteer-extra-plugin-stealth';

chromium.use(stealth());
```

This patches 20+ detection vectors automatically.

### Layer 2: Launch Args

```typescript
const browser = await chromium.launch({
  headless: true,
  args: [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--disable-gpu',
  ],
});
```

### Layer 3: Context Configuration

```typescript
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  viewport: {
    width: 1920 + Math.floor(Math.random() * 100),
    height: 1080 + Math.floor(Math.random() * 100),
  },
  locale: 'en-US',
  timezoneId: 'America/New_York',
  screen: { width: 1920, height: 1080 },
  geolocation: { longitude: -74.006, latitude: 40.7128 },
  permissions: ['geolocation'],
});
```

### Layer 4: Init Scripts

```typescript
await page.addInitScript(() => {
  // Remove webdriver flag
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
  });

  // Mock plugins (real Chrome has 3-5 plugins)
  Object.defineProperty(navigator, 'plugins', {
    get: () => [
      { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
      { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
      { name: 'Native Client', filename: 'internal-nacl-plugin' },
    ],
  });

  // Mock languages
  Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
  });

  // Consistent permissions
  const originalQuery = window.navigator.permissions.query;
  window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications'
      ? Promise.resolve({ state: Notification.permission })
      : originalQuery(parameters)
  );

  // Remove Chrome DevTools Protocol
  delete window.chrome;
});
```

### Layer 5: Human Behavior

```typescript
// Random delays
await page.waitForTimeout(1000 + Math.random() * 2000);

// Human-like mouse movement
async function humanClick(page, selector) {
  const element = await page.locator(selector);
  const box = await element.boundingBox();

  if (box) {
    const x = box.x + box.width * Math.random();
    const y = box.y + box.height * Math.random();

    await page.mouse.move(x, y, { steps: 10 });
    await page.waitForTimeout(100 + Math.random() * 200);
    await page.mouse.click(x, y, { delay: 50 + Math.random() * 100 });
  }
}
```

### Layer 6: User Agent Rotation

```typescript
const userAgents = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
];

const randomUA = userAgents[Math.floor(Math.random() * userAgents.length)];
```

**Important**: Match UA to actual Chrome version. Check https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome

## Verification Tools

Test your stealth setup:

- https://bot.sannysoft.com/ - Comprehensive bot detection test
- https://arh.antoinevastel.com/bots/areyouheadless - Headless detection
- https://pixelscan.net/ - Fingerprint analysis
- https://browserleaks.com/webrtc - WebRTC leak check

## Common Mistakes

| Mistake | Detection | Fix |
|---------|-----------|-----|
| Same UA every time | Pattern recognition | Rotate user agents |
| Fixed viewport | Fingerprinting | Randomize slightly |
| Instant actions | Bot-like speed | Add random delays |
| No cookies | Session tracking | Accept + persist cookies |
| Missing referer | Traffic analysis | Set referer header |
| Datacenter IP | IP reputation | Use residential proxy if needed |

## Advanced: Residential Proxies

If stealth mode alone isn't enough, add residential proxies:

```typescript
const context = await browser.newContext({
  proxy: {
    server: 'http://proxy-server:8080',
    username: 'user',
    password: 'pass',
  },
});
```

Providers: Bright Data, Oxylabs, Smartproxy ($$$ but effective)

## Site-Specific Bypasses

### Cloudflare

- Use stealth mode + residential IP
- Solve challenges with 2captcha/anti-captcha APIs
- Mimic real browser timing (5-10s wait after load)

### Google

- Respect robots.txt
- Add delays between searches (5-10s minimum)
- Use OAuth for authenticated APIs when possible

### LinkedIn

- Always login with real account
- Limit connections/views per day
- Use authenticated session pattern

## When Stealth Isn't Enough

If still getting blocked:
1. Verify at bot.sannysoft.com (should show all green)
2. Check IP reputation (https://www.abuseipdb.com/)
3. Consider solving CAPTCHAs programmatically
4. Contact site for API access (legal alternative)
