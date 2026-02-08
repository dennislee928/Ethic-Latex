# Common Blocking Patterns & Bypasses

Site-specific blocking patterns and proven workarounds.

## Cloudflare

### Detection Methods
- Navigator.webdriver check
- Timing analysis (page load to first action)
- TLS fingerprinting
- HTTP/2 fingerprinting
- JavaScript challenge

### Bypass Strategy

```typescript
import { chromium } from 'playwright-extra';
import stealth from 'puppeteer-extra-plugin-stealth';

chromium.use(stealth());

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-blink-features=AutomationControlled'],
});

const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  viewport: { width: 1920, height: 1080 },
});

const page = await context.newPage();

// CRITICAL: Wait 5-10 seconds after page load
await page.goto(url);
await page.waitForTimeout(8000); // Mimics human reading time

// Then interact
```

**Success Rate**: ~85% with residential IP, ~40% with datacenter IP

### When It Fails
- Use 2captcha or anti-captcha service
- Consider official API
- Rotate residential proxies

## Google

### Detection Methods
- Query rate limiting
- Account-based throttling
- Captcha challenges
- Search history analysis

### Bypass Strategy

```typescript
// Always add delays between requests
for (const query of queries) {
  await page.goto(`https://www.google.com/search?q=${encodeURIComponent(query)}`);

  const results = await page.$$eval('h3', (els) => els.map((e) => e.textContent));

  // CRITICAL: 10-15 second delay between searches
  await page.waitForTimeout(10000 + Math.random() * 5000);
}
```

**Better Alternative**: Use Google Custom Search API (official, legal)

## LinkedIn

### Detection Methods
- Login state verification
- Connection/view rate limiting
- Profile access patterns
- Account behavior analysis

### Bypass Strategy

```typescript
// Always use authenticated session
await page.goto('https://www.linkedin.com/login');
await page.fill('#username', process.env.LINKEDIN_EMAIL);
await page.fill('#password', process.env.LINKEDIN_PASSWORD);
await page.click('[type="submit"]');
await page.waitForURL('**/feed/', { timeout: 10000 });

// Save session
const cookies = await context.cookies();
await fs.writeFile('linkedin-session.json', JSON.stringify(cookies));

// Respect limits
// - Max 80-100 profile views per day
// - Max 20 connection requests per day
// - 3-5 second delay between actions
```

**Important**: LinkedIn Terms prohibit automated scraping. Use official API for legal access.

## Twitter/X

### Detection Methods
- Rate limiting by IP
- Account-based limits
- Guest token expiration

### Bypass Strategy

```typescript
// Use authenticated session
// Or use nitter.net (privacy-respecting frontend)

await page.goto('https://nitter.net/username');
const tweets = await page.$$eval('.tweet-content', (els) => els.map((e) => e.textContent));
```

**Better Alternative**: Twitter API v2 (official)

## Amazon

### Detection Methods
- Bot protection via Cloudflare/Akamai
- Price scraping detection
- High request volume

### Bypass Strategy

```typescript
// Always include proper headers
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  extraHTTPHeaders: {
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.amazon.com/',
  },
});

// Slow down (1 request per 3-5 seconds)
await page.waitForTimeout(3000 + Math.random() * 2000);
```

**Legal Note**: Amazon Terms prohibit scraping. Use Product Advertising API instead.

## Instagram

### Detection Methods
- Login requirement
- Rate limiting
- GraphQL query limits

### Bypass Strategy

```typescript
// Authenticated session required
await page.goto('https://www.instagram.com/accounts/login/');
await page.fill('[name="username"]', process.env.IG_USER);
await page.fill('[name="password"]', process.env.IG_PASS);
await page.click('[type="submit"]');

// Wait for 2FA if enabled
await page.waitForTimeout(15000);

// Respect limits (50-100 actions/hour max)
```

**Better Alternative**: Instagram Graph API (official)

## Facebook

### Detection Methods
- Mandatory login
- GraphQL query fingerprinting
- Account behavior analysis

### Bypass Strategy

Not recommended - Facebook actively blocks automation. Use Graph API for legal access.

## General E-Commerce Sites

### Detection Methods
- Session-based rate limiting
- Add-to-cart honeypots
- Price scraping detection

### Bypass Strategy

```typescript
// Respect robots.txt
const robotsTxt = await fetch(new URL('/robots.txt', url)).then((r) => r.text());

// Identify crawl-delay directive
const delayMatch = robotsTxt.match(/Crawl-delay:\s*(\d+)/i);
const delay = delayMatch ? parseInt(delayMatch[1]) * 1000 : 2000;

// Honor the delay
for (const product of products) {
  await page.goto(product.url);
  // Scrape...
  await page.waitForTimeout(delay);
}
```

## Captcha Bypasses

### hCaptcha / reCAPTCHA

**Option 1**: Solving services
- 2captcha.com (~$2.99/1000 solves)
- anti-captcha.com
- capsolver.com

**Option 2**: Avoid triggering
- Use residential IP
- Add human delays
- Limit requests
- Solve interactively once, persist session

### Example with 2captcha

```typescript
import fetch from 'node-fetch';

async function solve2Captcha(siteKey: string, pageUrl: string) {
  const apiKey = process.env.TWOCAPTCHA_KEY;

  // Submit captcha
  const submitResp = await fetch(`https://2captcha.com/in.php?key=${apiKey}&method=userrecaptcha&googlekey=${siteKey}&pageurl=${pageUrl}`);
  const submitText = await submitResp.text();
  const captchaId = submitText.split('|')[1];

  // Poll for solution (30s timeout)
  for (let i = 0; i < 30; i++) {
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const resultResp = await fetch(`https://2captcha.com/res.php?key=${apiKey}&action=get&id=${captchaId}`);
    const resultText = await resultResp.text();

    if (resultText.startsWith('OK|')) {
      return resultText.split('|')[1];
    }
  }

  throw new Error('Captcha timeout');
}

// Use in Playwright
const solution = await solve2Captcha('6Le-wvk...', page.url());
```

## IP Rotation

### Residential Proxies

```typescript
const proxies = [
  'http://user:pass@proxy1.example.com:8080',
  'http://user:pass@proxy2.example.com:8080',
];

for (const url of urls) {
  const proxy = proxies[Math.floor(Math.random() * proxies.length)];

  const context = await browser.newContext({
    proxy: { server: proxy },
  });

  const page = await context.newPage();
  await page.goto(url);
  // Scrape...
  await context.close();
}
```

### Datacenter Proxies

Cheaper but more likely to be blocked. Use only for low-security sites.

## Legal Considerations

| Site | Scraping Policy | Legal Alternative |
|------|-----------------|-------------------|
| Google | Terms prohibit scraping | Custom Search API |
| Twitter | Terms prohibit scraping | Twitter API v2 |
| LinkedIn | Terms prohibit scraping | LinkedIn API |
| Amazon | Terms prohibit scraping | Product Advertising API |
| Instagram | Terms prohibit scraping | Instagram Graph API |
| Facebook | Terms prohibit scraping | Facebook Graph API |

**Always check robots.txt and Terms of Service before scraping.**

## When All Else Fails

1. **Contact the site** - Ask for API access or data export
2. **Check for RSS feeds** - Many sites provide feeds
3. **Use official APIs** - Usually free tier available
4. **Consider alternatives** - Other data sources may exist
5. **Respect rate limits** - Don't overwhelm servers

**Remember**: Just because you CAN scrape doesn't mean you SHOULD.
