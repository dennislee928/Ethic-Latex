# Canonical URLs Reference

Canonical tags tell search engines which version of a page is the "main" one when duplicate or similar content exists.

## What is a Canonical URL?

The canonical URL is the preferred version of a page that you want search engines to index and rank.

**Format**:
```html
<link rel="canonical" href="https://example.com/page" />
```

**Location**: Always in `<head>` section.

## Why Canonicals Matter

### Without Canonical Tags

Your site has:
- https://example.com/services
- https://example.com/services/
- https://example.com/services?ref=nav
- https://www.example.com/services

Google sees 4 different pages, splits ranking signals between them.

### With Canonical Tags

All versions point to the canonical:
```html
<link rel="canonical" href="https://example.com/services" />
```

Google consolidates ranking signals to single URL.

## Self-Referencing Canonical

**Best Practice**: Every page should have a self-referencing canonical, even if no duplicates exist.

```html
<!-- On https://example.com/services -->
<link rel="canonical" href="https://example.com/services" />

<!-- On https://example.com/about -->
<link rel="canonical" href="https://example.com/about" />
```

**Benefits**:
- Prevents duplicate content issues from URL parameters
- Future-proofs against syndication
- Reinforces preferred URL format
- Required for some platforms (AMP, mobile versions)

## When to Use Canonical Tags

### 1. Duplicate Content

Multiple URLs serving same/similar content:

```html
<!-- Product page with color variations -->
<!-- /products/shirt?color=red -->
<!-- /products/shirt?color=blue -->
<!-- Both use canonical: -->
<link rel="canonical" href="https://example.com/products/shirt" />
```

### 2. Pagination

Blog archives, product listings with multiple pages:

```html
<!-- Page 2, 3, 4+ all point to page 1 -->
<!-- /blog?page=2 -->
<!-- /blog?page=3 -->
<link rel="canonical" href="https://example.com/blog" />
```

**Alternative**: Use `rel="prev"` and `rel="next"` (deprecated by Google 2019, but still supported by Bing).

### 3. Print/Mobile Versions

Separate URLs for print or mobile:

```html
<!-- On /services/print -->
<link rel="canonical" href="https://example.com/services" />

<!-- On m.example.com/services -->
<link rel="canonical" href="https://example.com/services" />
```

### 4. Tracking Parameters

URLs with query strings for tracking:

```html
<!-- /services?utm_source=facebook&utm_medium=social -->
<link rel="canonical" href="https://example.com/services" />
```

### 5. Syndicated Content

Content published on multiple domains:

```html
<!-- On partner-site.com/your-article -->
<link rel="canonical" href="https://your-site.com/article" />
```

**Note**: Cross-domain canonical. Tells search engines your site is original source.

### 6. WWW vs Non-WWW

Choose one as canonical:

```html
<!-- If www is canonical, on example.com: -->
<link rel="canonical" href="https://www.example.com/page" />

<!-- If non-www is canonical, on www.example.com: -->
<link rel="canonical" href="https://example.com/page" />
```

**Best Practice**: Also set up 301 redirect from non-canonical to canonical version.

### 7. HTTP vs HTTPS

Always use HTTPS as canonical:

```html
<!-- Even on http://example.com, use: -->
<link rel="canonical" href="https://example.com/page" />
```

**Best Practice**: Redirect all HTTP to HTTPS.

### 8. Trailing Slash Consistency

Choose one format:

```html
<!-- If /services/ is canonical: -->
<link rel="canonical" href="https://example.com/services/" />

<!-- If /services is canonical: -->
<link rel="canonical" href="https://example.com/services" />
```

**Best Practice**: Be consistent. Most sites prefer no trailing slash (except homepage).

## Canonical Tag Rules

### Always Use Absolute URLs

❌ **Wrong**: Relative URLs
```html
<link rel="canonical" href="/services" />
<link rel="canonical" href="../about" />
```

✅ **Right**: Absolute URLs
```html
<link rel="canonical" href="https://example.com/services" />
<link rel="canonical" href="https://example.com/about" />
```

### Only One Canonical Per Page

❌ **Wrong**: Multiple canonicals
```html
<link rel="canonical" href="https://example.com/services" />
<link rel="canonical" href="https://example.com/about" />
```

✅ **Right**: Single canonical
```html
<link rel="canonical" href="https://example.com/services" />
```

**If multiple exist**: Google chooses one, may not be your preferred version.

### Canonical Must Be Indexable

❌ **Wrong**: Canonical points to noindex page
```html
<meta name="robots" content="noindex" />
<link rel="canonical" href="https://example.com/services" />
```

✅ **Right**: Canonical points to indexable page (no noindex tag)

### Canonical Should Match Content

❌ **Wrong**: Canonical points to different content
```html
<!-- On /hot-water-repairs -->
<link rel="canonical" href="https://example.com/blocked-drains" />
```

✅ **Right**: Canonical points to same/similar content
```html
<!-- On /hot-water-repairs -->
<link rel="canonical" href="https://example.com/hot-water-repairs" />
```

### Canonical Should Be in <head>

❌ **Wrong**: Canonical in `<body>`
```html
<body>
  <link rel="canonical" href="https://example.com/services" />
</body>
```

✅ **Right**: Canonical in `<head>`
```html
<head>
  <link rel="canonical" href="https://example.com/services" />
</head>
```

## Common Mistakes

### 1. Missing Canonical Tag

**Problem**: Google may choose wrong URL as canonical.

**Fix**: Add self-referencing canonical to every page.

### 2. Relative URL in Canonical

**Problem**: May resolve incorrectly, especially on subdomains.

**Fix**: Always use absolute URLs starting with https://.

### 3. Canonical to Redirect

**Problem**: Page A canonicals to Page B, but Page B redirects to Page C.

**Fix**: Canonical should point directly to final destination (Page C).

### 4. Canonical Chain

**Problem**: Page A → Page B → Page C (chain of canonicals).

**Fix**: All pages should point to same final canonical (Page C).

### 5. Canonical to Different Content

**Problem**: Page about hot water repairs canonicals to page about blocked drains.

**Fix**: Only canonical to same/similar content.

### 6. Canonical and Noindex Together

**Problem**: Conflicting signals (canonical says "index this", noindex says "don't").

**Fix**: Remove one. If duplicate, use canonical only. If truly don't want indexed, use noindex only.

### 7. Paginated Content

**Problem**: All paginated pages canonical to page 1.

**Options**:
- Self-referencing canonical on each page (preferred by Google)
- View-all page as canonical (if you have one)

**Google Recommendation** (2019): Use self-referencing canonicals, not rel=prev/next.

## Testing Canonicals

### View Source

Check HTML source:
```html
<!-- Look for this in <head> -->
<link rel="canonical" href="..." />
```

### Chrome DevTools

1. Right-click page → Inspect
2. Go to Network tab
3. Select document (first item)
4. Check Response Headers for `Link: <...>; rel="canonical"`

### Screaming Frog

1. Crawl site
2. Go to "Canonicals" tab
3. Check for issues:
   - Missing canonicals
   - Non-indexable canonicals
   - Canonicals to redirects

### Google Search Console

**URL Inspection Tool**:
1. Enter URL
2. Check "User-declared canonical"
3. Check "Google-selected canonical"
4. If they differ, investigate why

## Canonical in HTTP Headers

For non-HTML files (PDFs, images), use HTTP header:

```
Link: <https://example.com/document.pdf>; rel="canonical"
```

**Example with Cloudflare Workers**:
```typescript
return new Response(pdfContent, {
  headers: {
    'Content-Type': 'application/pdf',
    'Link': '<https://example.com/document.pdf>; rel="canonical"'
  }
});
```

## Dynamic Canonicals

Generate canonical URLs from request data:

```tsx
// React/Next.js
export function SEOHead({ currentPath }) {
  const canonicalUrl = `${process.env.SITE_URL}${currentPath}`;

  return (
    <Helmet>
      <link rel="canonical" href={canonicalUrl} />
    </Helmet>
  );
}
```

```typescript
// Cloudflare Workers
const url = new URL(request.url);
const canonical = `${url.origin}${url.pathname}`;

const html = `
<!DOCTYPE html>
<html>
<head>
  <link rel="canonical" href="${canonical}" />
</head>
</html>
`;
```

## Canonical vs 301 Redirect

| Use Case | Canonical | 301 Redirect |
|----------|-----------|--------------|
| User sees different URLs | ✅ | ❌ (redirects to one) |
| Tracking parameters | ✅ | ❌ (breaks tracking) |
| Syndicated content | ✅ | ❌ (can't redirect others' sites) |
| Permanent URL change | ❌ | ✅ |
| WWW vs non-WWW | Both (redirect + canonical) | ✅ Primary |
| HTTP vs HTTPS | Both (redirect + canonical) | ✅ Primary |

**Best Practice**: Use 301 redirects for permanent changes, canonical for variations you want to keep accessible.

## Checklist

- [ ] Every page has canonical tag
- [ ] Canonical is absolute URL (https://...)
- [ ] Canonical is in `<head>` section
- [ ] Only one canonical per page
- [ ] Canonical points to indexable page (no noindex)
- [ ] Canonical matches content (not different page)
- [ ] Canonical doesn't point to redirect
- [ ] WWW/non-WWW handled consistently
- [ ] HTTP redirects to HTTPS
- [ ] Trailing slash handled consistently
- [ ] URL parameters stripped from canonical
- [ ] Matches og:url tag
- [ ] Tested with Google Search Console
- [ ] No canonical chains

## Examples by Page Type

### Homepage

```html
<link rel="canonical" href="https://example.com" />
```

**Note**: No trailing slash (convention), but either is fine if consistent.

### Service Page

```html
<link rel="canonical" href="https://example.com/services/hot-water-repairs" />
```

### Location Page

```html
<link rel="canonical" href="https://example.com/areas/bondi" />
```

### Blog Post

```html
<link rel="canonical" href="https://example.com/blog/5-plumbing-tips" />
```

### Paginated Archive

```html
<!-- Page 1: Self-referencing -->
<link rel="canonical" href="https://example.com/blog" />

<!-- Page 2+: Self-referencing (Google 2019 guidance) -->
<link rel="canonical" href="https://example.com/blog?page=2" />

<!-- Alternative: All point to page 1 (older practice) -->
<link rel="canonical" href="https://example.com/blog" />
```

---

**Production Note**: Generate canonical URLs from router/framework. Never hardcode. Always include even if you think no duplicates exist.
