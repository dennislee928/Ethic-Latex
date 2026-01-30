---
paths: "**/*.ts", "**/*browser*.ts", "**/*puppeteer*.ts", "**/*playwright*.ts"
---

# Cloudflare Browser Rendering Corrections

## MUST Pass env.MYBROWSER to launch()

```typescript
/* ❌ "Browser binding not passed" error */
import puppeteer from '@cloudflare/puppeteer'
const browser = await puppeteer.launch()

/* ✅ Pass the binding */
import puppeteer from '@cloudflare/puppeteer'
const browser = await puppeteer.launch(env.MYBROWSER)
```

## XPath Not Supported

```typescript
/* ❌ Security risk, not supported */
await page.$x('//button[@class="submit"]')

/* ✅ Use CSS selectors or page.evaluate() */
await page.$('button.submit')
// OR
await page.evaluate(() => {
  return document.evaluate(
    '//button[@class="submit"]',
    document,
    null,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null
  ).singleNodeValue
})
```

## disconnect() vs close()

```typescript
/* ❌ close() terminates session */
await browser.close() // Session ends

/* ✅ disconnect() keeps session alive */
ctx.waitUntil(browser.disconnect()) // Session reusable
```

## Use Tabs, Not Multiple Browsers

```typescript
/* ❌ Multiple browser instances */
const browser1 = await puppeteer.launch(env.MYBROWSER)
const browser2 = await puppeteer.launch(env.MYBROWSER)

/* ✅ Use multiple tabs in one browser */
const browser = await puppeteer.launch(env.MYBROWSER)
const page1 = await browser.newPage()
const page2 = await browser.newPage()
```

## Playwright Requires compatibility_date

```typescript
/* ✅ Playwright v1.55 GA (Sept 2025) */
// wrangler.jsonc:
{
  "compatibility_date": "2025-09-15" // Required for Playwright
}
```

## Session Reuse Pattern

```typescript
/* ✅ Reuse sessions for performance */
const sessionId = await env.MYBROWSER.sessions.create({ keep_alive: 60000 })
const browser = await puppeteer.connect(env.MYBROWSER, sessionId)

// Later requests can reconnect
const browser = await puppeteer.connect(env.MYBROWSER, existingSessionId)
```

## Browser Timeout

```typescript
/* ⚠️ Default 60 second timeout */
// For longer tasks, set keep_alive
const browser = await puppeteer.launch(env.MYBROWSER, {
  keep_alive: 300000, // 5 minutes
})
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `puppeteer.launch()` no args | `puppeteer.launch(env.MYBROWSER)` |
| `page.$x()` XPath | CSS selectors or `page.evaluate()` |
| `browser.close()` | `ctx.waitUntil(browser.disconnect())` |
| Multiple browsers | Multiple tabs in one browser |
| Playwright without date | Add `compatibility_date: "2025-09-15"` |
