# seo-meta

Generate complete SEO meta tags for every page including title patterns, meta descriptions, Open Graph tags, Twitter Cards, and JSON-LD structured data.

## Auto-Trigger Keywords

This skill should be suggested when the user mentions:

**Technology Names:**
- seo, search engine optimization, meta tags, metadata
- open graph, og tags, og:title, og:image, og:description
- twitter cards, twitter:card, social sharing, social media
- json-ld, structured data, schema.org, rich snippets, rich results
- canonical url, canonical tag

**Use Cases:**
- adding meta tags to pages
- implementing social sharing
- setting up structured data
- optimizing for search engines
- generating og:image tags
- implementing breadcrumbs schema
- adding LocalBusiness schema
- creating FAQ rich snippets
- implementing Service schema
- optimizing page titles
- writing meta descriptions

**HTML Elements:**
- `<title>` tag optimization
- `<meta name="description">` tag
- `<meta property="og:*">` tags
- `<meta name="twitter:*">` tags
- `<link rel="canonical">` tag
- `<script type="application/ld+json">` tag

**Common Tasks:**
- "add meta tags to this page"
- "implement open graph for social sharing"
- "add structured data for local business"
- "create SEO-friendly titles"
- "set up twitter cards"
- "add breadcrumb schema"
- "implement FAQ rich snippets"
- "optimize meta descriptions"
- "add canonical urls"
- "generate json-ld schema"

**Error Prevention:**
- title tag too long
- missing og:image
- duplicate titles across pages
- invalid json-ld syntax
- missing canonical tag
- wrong schema.org @type
- meta description too short/long
- relative urls in canonical
- multiple canonical tags
- missing twitter card type

## What This Skill Covers

1. **Title Tag Patterns** - Character limits, formulas by page type, modifiers
2. **Meta Descriptions** - Formulas, power words, examples by page type
3. **Open Graph Tags** - Required tags, image specifications, type values
4. **Twitter Cards** - Card types, required tags, fallback behavior
5. **JSON-LD Schemas** - LocalBusiness, Service, FAQ, BreadcrumbList
6. **Canonical URLs** - When to use, self-referencing, common mistakes
7. **Validation Tools** - Rich Results Test, Schema Validator, debuggers

## Quick Example

```tsx
<head>
  <title>Emergency Plumber Sydney | Acme Plumbing</title>
  <meta name="description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes. Call 1300 XXX XXX." />
  <link rel="canonical" href="https://acmeplumbing.com.au" />

  <meta property="og:title" content="Emergency Plumber Sydney" />
  <meta property="og:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service." />
  <meta property="og:image" content="https://acmeplumbing.com.au/og-image.jpg" />
  <meta property="og:url" content="https://acmeplumbing.com.au" />

  <script type="application/ld+json">
    {JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Plumber",
      "name": "Acme Plumbing",
      "telephone": "+61-XXX-XXX-XXX"
    })}
  </script>
</head>
```

## Related Skills

- tailwind-v4-shadcn (for UI components)
- cloudflare-worker-base (for SSR/meta generation)
- nextjs (for Head component and metadata)
- react-hook-form-zod (for form validation with structured data)
