# Open Graph Tags Reference

Open Graph (OG) tags control how your pages appear when shared on social media (Facebook, LinkedIn, WhatsApp, Slack, etc.).

## Required Tags

These 5 tags are **mandatory** for proper social sharing:

```html
<meta property="og:title" content="Service in Location" />
<meta property="og:description" content="Value prop. Differentiator. CTA." />
<meta property="og:image" content="https://example.com/og-image.jpg" />
<meta property="og:url" content="https://example.com/page" />
<meta property="og:type" content="website" />
```

### og:title

**Character Limit**: 60-70 characters (varies by platform)

**Best Practice**: Use same as page title, or shorter version without brand name.

**Examples**:
```html
<!-- Same as page title -->
<meta property="og:title" content="Emergency Plumber Sydney | Acme Plumbing" />

<!-- Shorter for social (if page title is long) -->
<meta property="og:title" content="Emergency Plumber Sydney" />
```

**Why it matters**: This is the headline users see when sharing. Make it compelling.

### og:description

**Character Limit**: 200-300 characters (more than meta description)

**Best Practice**: Can be same as meta description, or longer version with more detail.

**Examples**:
```html
<!-- Same as meta description -->
<meta property="og:description" content="Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes. Call 1300 XXX XXX." />

<!-- Longer version with more detail -->
<meta property="og:description" content="Fast emergency plumbing services across Sydney. Our licensed plumbers are available 24/7 for blocked drains, hot water repairs, leaks and gas fitting. Upfront quotes, same-day service, 1-year warranty on all work." />
```

**Why it matters**: This is the description under the headline. More space than meta description.

### og:image

**Required Dimensions**: 1200x630px (1.91:1 ratio)

**Critical Requirements**:
- Absolute URL (not relative)
- Publicly accessible (no auth required)
- HTTPS (not HTTP)
- Format: JPG or PNG (JPG preferred for smaller file size)
- File size: <1MB (ideally <300KB)

**Image Safe Zone**:
- Full image: 1200x630px
- Safe zone (always visible): 1000x530px center
- Keep text/logos in safe zone

**Examples**:
```html
<!-- Correct -->
<meta property="og:image" content="https://example.com/images/og-image.jpg" />

<!-- Wrong - relative URL -->
<meta property="og:image" content="/images/og-image.jpg" />

<!-- Wrong - HTTP not HTTPS -->
<meta property="og:image" content="http://example.com/og-image.jpg" />

<!-- Wrong - requires authentication -->
<meta property="og:image" content="https://example.com/admin/og-image.jpg" />
```

**Additional Image Properties** (optional but recommended):
```html
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Acme Plumbing emergency service van" />
```

**Why it matters**: Image is the most eye-catching element. Wrong size/format breaks social sharing.

### og:url

**Canonical URL**: Use the canonical URL of the page.

**Best Practice**: Always use absolute URLs, match canonical tag.

**Examples**:
```html
<!-- Correct -->
<meta property="og:url" content="https://example.com/services/hot-water" />

<!-- Wrong - relative URL -->
<meta property="og:url" content="/services/hot-water" />

<!-- Wrong - includes query parameters -->
<meta property="og:url" content="https://example.com/services/hot-water?ref=social" />
```

**Why it matters**: Prevents duplicate shares, ensures correct URL tracking.

### og:type

**Common Values**:

| Page Type | og:type Value |
|-----------|---------------|
| Home, Service, Location pages | website |
| Blog posts | article |
| Business profile | business.business |
| Product pages | product |
| Video pages | video.other |

**Examples**:
```html
<!-- Homepage -->
<meta property="og:type" content="website" />

<!-- Blog post -->
<meta property="og:type" content="article" />

<!-- Product page -->
<meta property="og:type" content="product" />
```

**Why it matters**: Platforms may display different UI based on type.

## Optional but Recommended Tags

### og:site_name

Brand name that appears above the title.

```html
<meta property="og:site_name" content="Acme Plumbing" />
```

### og:locale

Language/region code.

```html
<meta property="og:locale" content="en_AU" />
<meta property="og:locale" content="en_US" />
<meta property="og:locale" content="en_GB" />
```

### article:* (for blog posts)

Additional metadata for articles:

```html
<meta property="og:type" content="article" />
<meta property="article:published_time" content="2026-01-14T10:00:00+11:00" />
<meta property="article:modified_time" content="2026-01-14T15:30:00+11:00" />
<meta property="article:author" content="John Smith" />
<meta property="article:section" content="Plumbing Tips" />
<meta property="article:tag" content="hot water" />
<meta property="article:tag" content="maintenance" />
```

## Image Creation Guidelines

### Design Specifications

**Dimensions**: 1200x630px (exactly)
**Format**: JPG 80% quality or PNG
**File Size**: <300KB ideal, <1MB maximum
**Color Space**: sRGB

### Safe Zone for Text

```
┌─────────────────────────────────────┐
│         1200px width                │
│  ┌───────────────────────────────┐  │
│  │    1000px safe zone           │  │  630px
│  │    Keep text here             │  │  height
│  │                               │  │
│  └───────────────────────────────┘  │
│         100px margin each side      │
└─────────────────────────────────────┘
```

**Why safe zones matter**:
- Facebook crops to square on mobile
- LinkedIn crops to 1.91:1 but different safe zone
- WhatsApp shows different aspect ratio

### Text on Images

**Best Practices**:
- Font size: 72pt minimum (readable when scaled down)
- High contrast: Dark text on light background or vice versa
- Max 2 lines of text
- Logo in corner (not center)
- Brand colors for consistency

**Example Layout**:
```
┌─────────────────────────────────────┐
│  LOGO                               │
│                                     │
│      MAIN HEADLINE                  │
│      Secondary Text                 │
│                                     │
│                        acme.com.au  │
└─────────────────────────────────────┘
```

### Image Tools

**Online Generators**:
- Canva (template: 1200x630)
- Figma (OG image templates available)
- Adobe Express

**Optimization**:
- TinyPNG (lossy compression)
- ImageOptim (lossless)
- Cloudflare Images (automatic optimization)

**Testing**:
- Facebook Debugger (see preview)
- LinkedIn Post Inspector
- Twitter Card Validator

## Platform-Specific Requirements

### Facebook

**Image Requirements**:
- Min: 600x315px
- Recommended: 1200x630px
- Max file size: 8MB

**Notes**:
- Caches aggressively (use Debugger to clear)
- Crops to 1.91:1 on desktop, square on mobile
- Prefers JPG over PNG for load speed

### LinkedIn

**Image Requirements**:
- Min: 1200x627px
- Recommended: 1200x627px (slightly different ratio)
- Max file size: 5MB

**Notes**:
- Uses og:title and og:description
- Shows og:site_name above title
- Prefers professional-looking images

### WhatsApp

**Image Requirements**:
- Same as Facebook (1200x630px)
- Max file size: 300KB (compressed)

**Notes**:
- Heavy image compression
- Test on mobile device
- Simpler images work better

### Slack

**Image Requirements**:
- 1200x630px recommended
- Max file size: Not specified

**Notes**:
- Unfurls links automatically
- Shows title + description + image
- Respects og:site_name

## Testing & Validation

### Facebook Sharing Debugger

**URL**: https://developers.facebook.com/tools/debug/

**Use Cases**:
- Preview how your page will look when shared
- Clear Facebook's cache after updating OG tags
- Check for errors (missing tags, wrong image size)

**How to Use**:
1. Enter your URL
2. Click "Debug"
3. Review warnings/errors
4. Click "Scrape Again" after fixing issues

### LinkedIn Post Inspector

**URL**: https://www.linkedin.com/post-inspector/

**Use Cases**:
- Preview LinkedIn share appearance
- Clear LinkedIn's cache
- Validate og:title and og:description

### Twitter Card Validator

**URL**: https://cards-dev.twitter.com/validator

**Use Cases**:
- Preview Twitter Card (uses OG tags as fallback)
- Validate twitter:* tags
- Check image rendering

### Manual Testing

**Process**:
1. Update OG tags
2. Clear platform caches (use debugger tools)
3. Test share on each platform
4. Check mobile AND desktop
5. Verify image loads and text is readable

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
  <link rel="canonical" href="https://acmeplumbing.com.au" />

  <!-- Open Graph -->
  <meta property="og:title" content="Emergency Plumber Sydney" />
  <meta property="og:description" content="Fast emergency plumbing services across Sydney. Licensed plumbers available 24/7 for blocked drains, hot water repairs, leaks and gas fitting. Upfront quotes, same-day service, 1-year warranty." />
  <meta property="og:image" content="https://acmeplumbing.com.au/images/og-image.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Acme Plumbing emergency service van and licensed plumber" />
  <meta property="og:url" content="https://acmeplumbing.com.au" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Acme Plumbing" />
  <meta property="og:locale" content="en_AU" />
</head>
<body>
  <!-- Page content -->
</body>
</html>
```

## Common Mistakes

### Wrong Image Size

❌ **Wrong**: Using 800x600px image
✅ **Right**: 1200x630px exactly

**Result if wrong**: Image looks pixelated or gets cropped incorrectly.

### Relative URLs

❌ **Wrong**: `og:image` content="/images/og.jpg"
✅ **Right**: `og:image` content="https://example.com/images/og.jpg"

**Result if wrong**: Image doesn't load on social platforms.

### Missing og:image

❌ **Wrong**: No `og:image` tag
✅ **Right**: Always include `og:image`

**Result if wrong**: Platform uses random image from page or no image.

### Duplicate Content

❌ **Wrong**: Same og:title on every page
✅ **Right**: Unique og:title per page

**Result if wrong**: All shares look identical, poor click-through.

### Not Testing

❌ **Wrong**: Deploy without checking Facebook Debugger
✅ **Right**: Test on all platforms before launch

**Result if wrong**: Broken shares, poor user experience.

## Dynamic OG Tags (React Example)

```tsx
import { Helmet } from 'react-helmet-async';

export function SEOHead({ page }) {
  const ogImage = `${process.env.SITE_URL}/images/og/${page.slug}.jpg`;

  return (
    <Helmet>
      <title>{page.title} | Acme Plumbing</title>
      <meta name="description" content={page.description} />
      <link rel="canonical" href={`${process.env.SITE_URL}${page.path}`} />

      {/* Open Graph */}
      <meta property="og:title" content={page.ogTitle || page.title} />
      <meta property="og:description" content={page.ogDescription || page.description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:url" content={`${process.env.SITE_URL}${page.path}`} />
      <meta property="og:type" content={page.type || 'website'} />
      <meta property="og:site_name" content="Acme Plumbing" />
      <meta property="og:locale" content="en_AU" />
    </Helmet>
  );
}
```

## Checklist

- [ ] All 5 required tags present (title, description, image, url, type)
- [ ] Image is 1200x630px exactly
- [ ] Image is <300KB file size
- [ ] All URLs are absolute (https://)
- [ ] og:url matches canonical tag
- [ ] Unique og:title per page
- [ ] Unique og:description per page
- [ ] Tested with Facebook Debugger
- [ ] Tested with LinkedIn Post Inspector
- [ ] Tested on mobile devices
- [ ] Text in image is readable when scaled down

---

**Production Note**: Generate OG images dynamically using templates. Store in CDN/R2 for fast loading.
