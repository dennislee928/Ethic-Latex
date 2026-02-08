# Twitter Cards Reference

Twitter Cards control how your links appear on Twitter/X. They use `twitter:*` meta tags but fall back to Open Graph tags if twitter-specific tags are missing.

## Card Types

Twitter supports several card types. For most websites, use one of these two:

### summary

Small square image (1:1 ratio), basic info.

**Use Cases**:
- Blog posts without featured image
- Profile/about pages
- Pages where image isn't the focus

**Appearance**:
```
┌────────────────────────────┐
│  [Image]  Title            │
│  (144x144) Description     │
│           domain.com       │
└────────────────────────────┘
```

### summary_large_image

Large image (1.91:1 ratio), most common.

**Use Cases**:
- Homepage
- Service pages
- Blog posts with featured image
- Any page where visual is important

**Appearance**:
```
┌────────────────────────────┐
│                            │
│     [Large Image]          │
│     (1200x628)             │
│                            │
├────────────────────────────┤
│ Title                      │
│ Description                │
│ domain.com                 │
└────────────────────────────┘
```

**Best Practice**: Use `summary_large_image` by default unless you have a specific reason for `summary`.

## Required Tags

### Minimum Required Tags

```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Service in Location" />
<meta name="twitter:description" content="Value prop. Differentiator. CTA." />
<meta name="twitter:image" content="https://example.com/twitter-image.jpg" />
```

### All Available Tags

```html
<!-- Card type -->
<meta name="twitter:card" content="summary_large_image" />

<!-- Content -->
<meta name="twitter:title" content="Emergency Plumber Sydney" />
<meta name="twitter:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes." />
<meta name="twitter:image" content="https://example.com/images/twitter-image.jpg" />
<meta name="twitter:image:alt" content="Acme Plumbing emergency service van" />

<!-- Attribution (optional) -->
<meta name="twitter:site" content="@acmeplumbing" />
<meta name="twitter:creator" content="@johnsmith" />
```

## Tag Details

### twitter:card

**Values**: `summary`, `summary_large_image`, `app`, `player`

**Most Common**: `summary_large_image`

**Examples**:
```html
<!-- Large image card (most common) -->
<meta name="twitter:card" content="summary_large_image" />

<!-- Small image card -->
<meta name="twitter:card" content="summary" />
```

### twitter:title

**Character Limit**: 70 characters

**Best Practice**: Use same as `og:title` or shorter version.

**Examples**:
```html
<!-- Same as page title -->
<meta name="twitter:title" content="Emergency Plumber Sydney | Acme Plumbing" />

<!-- Shorter for social -->
<meta name="twitter:title" content="Emergency Plumber Sydney" />
```

### twitter:description

**Character Limit**: 200 characters

**Best Practice**: Use same as `og:description` or customized version.

**Examples**:
```html
<!-- Same as OG description -->
<meta name="twitter:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes. Call 1300 XXX XXX." />

<!-- Twitter-specific version -->
<meta name="twitter:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service. DM us or call 1300 XXX XXX." />
```

### twitter:image

**summary_large_image Requirements**:
- Min: 300x157px
- Recommended: 1200x628px (same as OG image)
- Max: 4096x4096px
- Max file size: 5MB
- Format: JPG, PNG, WEBP, GIF

**summary Requirements**:
- Min: 144x144px
- Recommended: 400x400px
- Square aspect ratio (1:1)

**Best Practice**: Use same image as `og:image` (1200x630px) for consistency.

**Examples**:
```html
<!-- Use same as OG image -->
<meta name="twitter:image" content="https://example.com/images/og-image.jpg" />

<!-- Twitter-specific image -->
<meta name="twitter:image" content="https://example.com/images/twitter-image.jpg" />
```

### twitter:image:alt

**Character Limit**: 420 characters

**Best Practice**: Describe the image for accessibility.

**Examples**:
```html
<meta name="twitter:image:alt" content="Acme Plumbing emergency service van and licensed plumber in Sydney" />
<meta name="twitter:image:alt" content="Modern hot water system installation by Acme Plumbing" />
```

### twitter:site

**Format**: @username of the website/brand

**Optional but Recommended**: Helps with attribution and analytics.

**Examples**:
```html
<meta name="twitter:site" content="@acmeplumbing" />
<meta name="twitter:site" content="@jezweb" />
```

### twitter:creator

**Format**: @username of the content creator/author

**Use Case**: Blog posts, articles with individual authors.

**Examples**:
```html
<!-- Blog post author -->
<meta name="twitter:creator" content="@johnsmith" />

<!-- Same as site for business pages -->
<meta name="twitter:creator" content="@acmeplumbing" />
```

## Fallback Behavior

Twitter Cards fall back to Open Graph tags when twitter-specific tags are missing:

| Missing Tag | Fallback |
|-------------|----------|
| `twitter:title` | Uses `og:title` |
| `twitter:description` | Uses `og:description` |
| `twitter:image` | Uses `og:image` |

**Implication**: You can skip twitter:* tags if OG tags are comprehensive.

## Minimal vs Complete Setup

### Minimal Setup (OG Tags Only)

If you have complete Open Graph tags, Twitter will use them:

```html
<!-- Open Graph only -->
<meta property="og:title" content="Emergency Plumber Sydney" />
<meta property="og:description" content="Fast emergency plumbing in Sydney." />
<meta property="og:image" content="https://example.com/og-image.jpg" />

<!-- Twitter will render using OG tags above -->
```

**Result**: Twitter shows card with OG data.

### Complete Setup (Twitter-Specific)

Add twitter:* tags when you want different content for Twitter:

```html
<!-- Open Graph -->
<meta property="og:title" content="Emergency Plumber Sydney | Acme Plumbing" />
<meta property="og:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes. Call 1300 XXX XXX." />
<meta property="og:image" content="https://example.com/og-image.jpg" />

<!-- Twitter-specific (different content) -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Emergency Plumber Sydney 🚰" />
<meta name="twitter:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7. DM or call 1300 XXX XXX. #SydneyPlumber" />
<meta name="twitter:image" content="https://example.com/twitter-specific.jpg" />
<meta name="twitter:site" content="@acmeplumbing" />
```

**When to Use Different Content**:
- Twitter audience differs from general audience
- Want to include hashtags/mentions
- Want shorter, more casual tone
- Have Twitter-optimized image

## Testing & Validation

### Twitter Card Validator

**URL**: https://cards-dev.twitter.com/validator

**Note**: As of 2024, Twitter/X has restricted access to Card Validator. You may need to be logged in or have developer access.

**How to Use**:
1. Enter your URL
2. Click "Preview card"
3. Review appearance (title, description, image)
4. Check for errors/warnings

**Alternative Testing**:
- Post link in Twitter DM to yourself
- Use third-party tools (Metatags.io, OpenGraph.xyz)
- Check with browser extension (META SEO inspector)

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| No card shown | Missing twitter:card tag | Add `<meta name="twitter:card" content="summary_large_image" />` |
| Blank image | Image URL wrong/inaccessible | Use absolute HTTPS URL, check file exists |
| Truncated text | Title/description too long | Keep title <70 chars, description <200 chars |
| Wrong card type | Card type doesn't match content | Use summary_large_image for most pages |

## Complete Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Basic SEO -->
  <title>Emergency Plumber Sydney | Acme Plumbing</title>
  <meta name="description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes. Call 1300 XXX XXX." />

  <!-- Open Graph -->
  <meta property="og:title" content="Emergency Plumber Sydney" />
  <meta property="og:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes." />
  <meta property="og:image" content="https://acmeplumbing.com.au/images/og-image.jpg" />
  <meta property="og:url" content="https://acmeplumbing.com.au" />
  <meta property="og:type" content="website" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Emergency Plumber Sydney" />
  <meta name="twitter:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7. Call 1300 XXX XXX or DM us." />
  <meta name="twitter:image" content="https://acmeplumbing.com.au/images/og-image.jpg" />
  <meta name="twitter:image:alt" content="Acme Plumbing emergency service van with licensed plumber in Sydney" />
  <meta name="twitter:site" content="@acmeplumbing" />
</head>
<body>
  <!-- Page content -->
</body>
</html>
```

## Best Practices

### Use summary_large_image by Default

Unless you have a specific reason, always use `summary_large_image`:
- More visually appealing
- Higher click-through rate
- Better for brand recognition
- Same image size as OG (1200x630)

### Reuse OG Images

Don't create separate Twitter images unless necessary:
- OG image dimensions (1200x630) work perfectly for Twitter
- Saves storage and reduces complexity
- Ensures consistent branding

### Include twitter:site

If you have a Twitter account, always include `twitter:site`:
- Shows brand attribution
- Helps with analytics
- Adds credibility

### Keep Descriptions Concise

Twitter descriptions have 200 char limit but shorter is better:
- Mobile users see less text
- Shorter = more impact
- Leave room for tweet text above card

## Common Mistakes

### Missing twitter:card Tag

❌ **Wrong**: No `twitter:card` tag
✅ **Right**: `<meta name="twitter:card" content="summary_large_image" />`

**Result if wrong**: Twitter doesn't show card, just plain link.

### Using property Instead of name

❌ **Wrong**: `<meta property="twitter:card" content="..." />`
✅ **Right**: `<meta name="twitter:card" content="..." />`

**Result if wrong**: Tag not recognized, card doesn't render.

### Wrong Image Size

❌ **Wrong**: Using 600x400px image for summary_large_image
✅ **Right**: 1200x628px minimum

**Result if wrong**: Image looks pixelated or gets cropped badly.

### Relative Image URLs

❌ **Wrong**: `twitter:image` content="/images/card.jpg"
✅ **Right**: `twitter:image` content="https://example.com/images/card.jpg"

**Result if wrong**: Image doesn't load.

## When to Skip Twitter Tags

You can skip twitter:* tags entirely if:
- Your OG tags are comprehensive
- You want same content on all platforms
- You don't have Twitter account (@site tag)
- You want to minimize meta tag bloat

**Fallback Behavior**: Twitter will use OG tags and render correctly.

## Dynamic Twitter Cards (React Example)

```tsx
import { Helmet } from 'react-helmet-async';

export function SEOHead({ page, twitterAccount }) {
  return (
    <Helmet>
      {/* Open Graph */}
      <meta property="og:title" content={page.title} />
      <meta property="og:description" content={page.description} />
      <meta property="og:image" content={page.image} />

      {/* Twitter Card - only if different from OG */}
      {page.twitterTitle && (
        <meta name="twitter:title" content={page.twitterTitle} />
      )}
      {page.twitterDescription && (
        <meta name="twitter:description" content={page.twitterDescription} />
      )}

      {/* Always include card type and site */}
      <meta name="twitter:card" content="summary_large_image" />
      {twitterAccount && (
        <meta name="twitter:site" content={`@${twitterAccount}`} />
      )}
    </Helmet>
  );
}
```

## Checklist

- [ ] `twitter:card` tag present (usually summary_large_image)
- [ ] Image is 1200x628px (or 400x400 for summary)
- [ ] Image URL is absolute (https://)
- [ ] Title is <70 characters
- [ ] Description is <200 characters
- [ ] `twitter:site` included (if have Twitter account)
- [ ] Tested with Twitter Card Validator (or manual tweet test)
- [ ] Fallback to OG tags works if twitter tags missing
- [ ] Image has alt text (`twitter:image:alt`)

---

**Production Note**: Start with OG tags only. Add twitter:* tags later if you need Twitter-specific content or have a Twitter account for attribution.
