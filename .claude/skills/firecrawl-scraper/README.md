# Firecrawl Web Scraper

**Status**: Production Ready
**Last Updated**: 2026-01-20
**API Version**: v2
**Official Docs**: https://docs.firecrawl.dev

---

## What This Skill Does

Provides complete knowledge for using Firecrawl API - a web data platform that converts websites into LLM-ready markdown or structured data. This skill covers:

- **Single page scraping** with `/scrape` endpoint
- **Full site crawling** with `/crawl` endpoint
- **URL discovery** with `/map` endpoint
- **Web search + scrape** with `/search` endpoint (NEW)
- **Structured data extraction** with `/extract` endpoint
- **Autonomous AI agent** with `/agent` endpoint (NEW)
- **Batch operations** for multiple URLs (NEW)
- **Change tracking** to monitor content changes (NEW)
- **Branding extraction** for design systems (NEW)
- **Python SDK** (firecrawl-py v4.13.0+)
- **TypeScript/Node.js SDK** (@mendable/firecrawl-js v4.11.1+)
- **JavaScript rendering**, anti-bot bypass, PDF/DOCX parsing
- **Cloudflare Workers integration** (REST API)

**Prevents common issues** with API authentication, rate limiting, timeout errors, and content extraction failures.

---

## Auto-Trigger Keywords

Claude automatically uses this skill when you mention:

### Primary Triggers (Technologies)
- firecrawl
- firecrawl api
- firecrawl-py
- firecrawl-js
- web scraping
- web crawler
- site crawler
- scrape website
- crawl website
- web scraper
- firecrawl agent
- firecrawl search

### Secondary Triggers (Use Cases)
- extract web content
- html to markdown
- convert website to markdown
- scrape documentation
- crawl documentation site
- extract structured data
- parse website
- content extraction
- web automation
- website to llm
- llm ready data
- rag from website
- scrape articles
- extract product data
- map website urls
- batch scrape
- scrape multiple urls
- monitor website changes
- track content changes
- extract brand colors
- extract design system
- autonomous web scraping
- ai web agent

### Error-Based Triggers
- "content not loading"
- "javascript rendering issues"
- "blocked by bot detection"
- "scraping blocked"
- "captcha blocking scraper"
- "dynamic content not scraping"
- "anti-bot protection"
- "scraper detected"
- "cloudflare challenge"
- "timeout scraping"
- "empty scrape result"
- "rate limit exceeded firecrawl"
- "invalid api key firecrawl"

### Framework Integration
- firecrawl cloudflare workers
- firecrawl python
- firecrawl typescript
- firecrawl node.js
- scraping with cloudflare
- serverless web scraping

---

## Known Issues Prevented

| Issue | Error Message | Prevention |
|-------|---------------|------------|
| **#1: API Key Not Set** | "Invalid API Key" | Proper environment variable setup |
| **#2: Rate Limits** | "Rate limit exceeded" | Credit optimization best practices |
| **#3: Timeout Errors** | "Request timeout" | `waitFor` and `timeout` configuration |
| **#4: Empty Content** | "Content is empty" | JS rendering with actions/wait |
| **#5: Bot Detection** | "Access denied" | Stealth mode and location options |
| **#6: Hardcoded API Keys** | Security vulnerability | Environment variable patterns |

---

## API Endpoints Overview

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `/scrape` | Single page | Extract article, product page |
| `/crawl` | Full site | Index docs, archive sites |
| `/map` | URL discovery | Find all pages, plan strategy |
| `/search` | Web search + scrape | Research with live data |
| `/extract` | Structured data | Product prices, contacts |
| `/agent` | Autonomous AI | No URLs needed, AI navigates |
| `/batch-scrape` | Multiple URLs | Bulk processing |

---

## Quick Start

### Python

```bash
pip install firecrawl-py
export FIRECRAWL_API_KEY=fc-your-api-key
```

```python
from firecrawl import Firecrawl
import os

app = Firecrawl(api_key=os.environ.get("FIRECRAWL_API_KEY"))

# Scrape single page
doc = app.scrape(
    url="https://example.com",
    formats=["markdown"],
    only_main_content=True
)

print(doc.markdown)
```

### TypeScript/Node.js

```bash
npm install @mendable/firecrawl-js
export FIRECRAWL_API_KEY=fc-your-api-key
```

```typescript
import FirecrawlApp from '@mendable/firecrawl-js';

const app = new FirecrawlApp({ apiKey: process.env.FIRECRAWL_API_KEY });

const result = await app.scrapeUrl('https://example.com', {
  formats: ['markdown'],
  onlyMainContent: true
});

console.log(result.markdown);
```

**Full instructions**: See `SKILL.md`

---

## Cloudflare Workers Compatibility

**The Firecrawl SDK cannot run in Cloudflare Workers** (requires Node.js).

**For Cloudflare Workers**, use the REST API directly with `fetch`:

```typescript
const response = await fetch('https://api.firecrawl.dev/v2/scrape', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${env.FIRECRAWL_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ url, formats: ['markdown'] })
});
```

See **Cloudflare Workers Integration** section in `SKILL.md` for complete examples.

---

## Package Versions (Verified 2026-01-20)

| Package | Version | Status |
|---------|---------|--------|
| firecrawl-py | 4.13.0+ | Latest stable |
| @mendable/firecrawl-js | 4.11.1+ | Latest stable |
| API Version | v2 | Current |

---

## When to Use This Skill

**Use this skill when:**
- Scraping modern websites with JavaScript
- Converting websites to markdown for RAG/LLMs
- Extracting structured data from web pages
- Performing web search + scrape in one call
- Autonomous data gathering without URLs (Agent)
- Monitoring content changes over time
- Batch processing multiple URLs
- Extracting brand/design systems
- Need to bypass bot protection

**Don't use this skill for:**
- Simple static HTML scraping (use BeautifulSoup/Cheerio)
- APIs with official SDKs (use the SDK directly)
- Sites you control (just export the data)

---

## Token Savings Estimate

**Without this skill**: ~10,000 tokens (API docs lookup + trial-and-error)
**With this skill**: ~3,500 tokens (direct implementation)

**Savings**: ~65% token reduction + prevents common issues

---

## Official Documentation

- **Docs**: https://docs.firecrawl.dev
- **Python SDK**: https://docs.firecrawl.dev/sdks/python
- **Node.js SDK**: https://docs.firecrawl.dev/sdks/node
- **API Reference**: https://docs.firecrawl.dev/api-reference
- **GitHub**: https://github.com/mendableai/firecrawl
- **Get API Key**: https://www.firecrawl.dev

---

## Next Steps After Using This Skill

1. **Store scraped data**: Use `cloudflare-d1` skill for database storage
2. **Build vector search**: Use `cloudflare-vectorize` skill for RAG
3. **Schedule scraping**: Use `cloudflare-queues` skill for async jobs
4. **Process with AI**: Use `cloudflare-workers-ai` skill for content analysis

---

**Production Tested**: Yes
**Token Efficiency**: ~65% savings
**Error Prevention**: 6 common issues prevented
**Composable**: Works with other Cloudflare skills
