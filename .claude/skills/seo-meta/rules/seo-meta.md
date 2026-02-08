# SEO Meta Tags Corrections

## Title Tag Patterns

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| "Welcome to [Brand]" in title | Start with service/value prop |
| Title >60 characters | Keep under 60 chars for full display |
| Same title on multiple pages | Unique title per page |
| Generic "Home" or "Services" | Specific: "Emergency Plumber Sydney \| Brand" |
| ALL CAPS title | Title case (first letter caps) |

## Meta Description Patterns

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Description >160 characters | Keep 150-160 chars (desktop), 120-130 (mobile) |
| No call to action | End with CTA: "Call 1300 XXX XXX" or "Book online" |
| Same description on all pages | Unique description per page |
| Keyword stuffing | Natural language with 1-2 keywords |
| No differentiator | Include USP: "24/7 service", "upfront pricing" |

## Open Graph Tags

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Missing og:image | Always include og:image (1200x630px) |
| Relative URL in og:image | Absolute URL: "https://example.com/og-image.jpg" |
| Wrong image size | 1200x630px (1.91:1 ratio) |
| Missing og:type | Include: "website" (pages) or "article" (blog) |
| Different og:url and canonical | Match og:url to canonical tag |

## JSON-LD Structured Data

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Generic @type "LocalBusiness" | Specific: "Plumber", "Electrician", "Locksmith" |
| Missing required fields | Include: name, @id, url, address, telephone |
| Relative URLs in schema | Absolute URLs starting with https:// |
| Date format "DD/MM/YYYY" | ISO 8601: "2026-01-14T10:00:00+11:00" |
| Missing @context | Always include: "@context": "https://schema.org" |

## Canonical URLs

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| No canonical tag | Every page needs self-referencing canonical |
| Relative URL in canonical | Absolute URL: "https://example.com/page" |
| Multiple canonical tags | Only one canonical per page |
| Canonical to redirect | Point directly to final destination |
| Canonical with query parameters | Strip params: /page not /page?ref=nav |

## Common Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|--------------|----------------|-----------------|
| "Welcome to..." in title | Wastes 11 characters | Start with service/value |
| Emoji in title/description | Breaks in search results | Use text only |
| Keyword stuffing | Looks spammy, hurts ranking | Natural language, 1-2 mentions |
| Missing og:image | Breaks social sharing | Always include (1200x630px) |
| Generic schema @type | Doesn't help SEO | Use specific type (Plumber not LocalBusiness) |
| Duplicate titles | Confuses search engines | Unique title per page |
| Description without CTA | Missed opportunity | End with clear CTA |

## Page Type Patterns

### Homepage

```tsx
// Title Pattern
"[Brand] - [Primary Service] in [Location]"
// Example: Acme Plumbing - 24/7 Emergency Plumber Sydney

// Description Pattern
"[Value prop] [Service] in [Location]. [Differentiator]. [CTA]."
// Example: Fast, reliable plumbing services in Sydney. 24/7 emergency response, licensed plumbers, upfront pricing. Call 1300 XXX XXX for same-day service.

// Schema
@type: "Plumber" (specific, not LocalBusiness)
```

### Service Page

```tsx
// Title Pattern
"[Service] in [Location] | [Brand]"
// Example: Hot Water Repairs Sydney | Acme Plumbing

// Description Pattern
"[Specific Service] in [Location]. [Service Details]. [Differentiator]. [CTA]."
// Example: Expert hot water repairs in Sydney. Fix or replace electric, gas & solar systems. Licensed technicians, 1-year warranty. Book online or call 1300 XXX XXX.

// Schema
@type: "Service"
Include: provider, areaServed, availableChannel
```

### Location Page

```tsx
// Title Pattern
"[Service] [Suburb] | [Brand]"
// Example: Plumber Bondi | Acme Plumbing

// Description Pattern
"[Service] in [Suburb]. [Service Types]. [Differentiator]. [Local CTA]."
// Example: Trusted plumber in Bondi. Blocked drains, leaks, hot water, gas fitting. Same-day service, upfront quotes. Call your local plumber on 1300 XXX XXX.
```

## Character Limits Quick Reference

| Element | Desktop | Mobile | Best Practice |
|---------|---------|--------|---------------|
| Title | 50-60 chars | ~78 chars | Keep under 60 |
| Meta Description | 155-160 chars | 120-130 chars | 150-160, front-load key info |
| og:title | 60-70 chars | Varies | Match page title or shorter |
| og:description | 200-300 chars | Varies | Can be longer than meta |
| twitter:title | 70 chars | Same | Can match OG or shorter |

## Validation Checklist

Before deploying, verify:

- [ ] Title is unique and <60 characters
- [ ] Description is unique and 150-160 characters
- [ ] Description includes CTA
- [ ] Canonical tag present (absolute URL)
- [ ] og:image present (1200x630px, absolute URL)
- [ ] og:url matches canonical
- [ ] JSON-LD has specific @type (not generic)
- [ ] JSON-LD has all required fields
- [ ] All URLs are absolute (https://)
- [ ] No duplicate titles across pages
- [ ] No "Welcome to..." in title
- [ ] Tested with Google Rich Results Test
- [ ] Tested with Facebook Debugger

## Testing Tools

| Tool | Use For | URL |
|------|---------|-----|
| Google Rich Results Test | Validate JSON-LD | search.google.com/test/rich-results |
| Schema Markup Validator | Validate schema syntax | validator.schema.org |
| Facebook Debugger | Test Open Graph | developers.facebook.com/tools/debug |
| Twitter Card Validator | Test Twitter Cards | cards-dev.twitter.com/validator |

## Production Workflow

1. **Generate meta tags** from CMS/database (never hardcode)
2. **Validate** with Rich Results Test before deploying
3. **Test social sharing** with Facebook/Twitter debuggers
4. **Monitor** Search Console for indexing issues
5. **Update** when business details change (hours, phone, services)

---

**Source**: Schema.org, Open Graph Protocol, Google Search Central
