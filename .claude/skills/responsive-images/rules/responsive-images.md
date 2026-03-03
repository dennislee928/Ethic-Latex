# Responsive Images Corrections

## Always Use srcset for Images >400px

**Problem**: Single-size images waste bandwidth on mobile and look pixelated on retina displays.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<img src="/image.jpg">` | `<img srcset="... 400w, ... 800w, ... 1200w" sizes="...">` |

```html
<!-- ❌ WRONG - wastes bandwidth, no retina support -->
<img src="/image-1200.jpg" alt="Image" />

<!-- ✅ CORRECT - responsive sizes -->
<img
  src="/image-800.jpg"
  srcset="
    /image-400.jpg 400w,
    /image-800.jpg 800w,
    /image-1200.jpg 1200w
  "
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Image"
  width="800"
  height="600"
  loading="lazy"
/>
```

**Exception**: Small fixed-size images like logos (<200px) can use density descriptors or single size.

## Always Use Lazy Loading for Below-Fold Images

**Problem**: Loading all images immediately delays page load and LCP.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<img src="...">` (no loading attr) | `<img src="..." loading="lazy">` |
| `loading="lazy"` on hero image | `loading="eager" fetchpriority="high"` |

```html
<!-- ❌ WRONG - loads all images immediately -->
<img src="/content-image.jpg" alt="Content" />

<!-- ✅ CORRECT - defers below-fold images -->
<img src="/content-image.jpg" alt="Content" loading="lazy" />

<!-- ✅ CORRECT - prioritizes LCP image -->
<img
  src="/hero.jpg"
  alt="Hero"
  loading="eager"
  fetchpriority="high"
/>
```

## Always Include Alt Text

**Problem**: Fails accessibility, SEO, and screen reader support.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<img src="...">` | `<img src="..." alt="Descriptive text">` |
| `alt="image"` | Descriptive alt text |
| Missing alt on decorative images | `alt="" role="presentation"` |

```html
<!-- ❌ WRONG -->
<img src="/product.jpg" />
<img src="/product.jpg" alt="image" />

<!-- ✅ CORRECT - descriptive alt -->
<img src="/product.jpg" alt="Red leather messenger bag with brass buckles" />

<!-- ✅ CORRECT - decorative images -->
<img src="/decorative-line.svg" alt="" role="presentation" />
```

## Always Prevent Layout Shift (Aspect Ratio or Dimensions)

**Problem**: Images loading without reserved space cause layout shift, hurting CLS score.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<img src="...">` (no dimensions) | `<img src="..." width="..." height="...">` |
| Container without aspect-ratio | `<div class="aspect-[16/9]">` |

```html
<!-- ❌ WRONG - causes layout shift -->
<img src="/image.jpg" alt="Image" loading="lazy" />

<!-- ✅ CORRECT - explicit dimensions -->
<img
  src="/image.jpg"
  alt="Image"
  width="800"
  height="600"
  loading="lazy"
/>

<!-- ✅ CORRECT - aspect-ratio container -->
<div class="aspect-[16/9]">
  <img
    src="/image.jpg"
    alt="Image"
    width="800"
    height="450"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</div>
```

## Never Use loading="lazy" on LCP Images

**Problem**: Delays Largest Contentful Paint, hurting Core Web Vitals score.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `loading="lazy"` on hero/first image | `loading="eager" fetchpriority="high"` |

```html
<!-- ❌ WRONG - delays LCP -->
<img
  src="/hero.jpg"
  alt="Hero"
  loading="lazy"
/>

<!-- ✅ CORRECT - prioritizes LCP -->
<img
  src="/hero.jpg"
  alt="Hero"
  loading="eager"
  fetchpriority="high"
/>
```

**Rule of Thumb**: First 2-3 images visible on page load should be `loading="eager"`.

## Use fetchpriority="high" for Hero Images

**Problem**: LCP image competes with other resources, delaying load.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Hero image without fetchpriority | `fetchpriority="high"` |

```html
<!-- ❌ WRONG - no priority boost -->
<img
  src="/hero.jpg"
  alt="Hero"
  loading="eager"
/>

<!-- ✅ CORRECT - prioritizes download -->
<img
  src="/hero.jpg"
  alt="Hero"
  loading="eager"
  fetchpriority="high"
/>
```

## Use Width Descriptors (w), Not Density (x) for Responsive Images

**Problem**: Browser can't optimize for viewport size.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `srcset="... 1x, ... 2x"` for content images | `srcset="... 400w, ... 800w" sizes="..."` |

```html
<!-- ❌ WRONG - only considers DPR, not viewport -->
<img
  src="/image.jpg"
  srcset="/image.jpg 1x, /image@2x.jpg 2x"
  alt="Image"
/>

<!-- ✅ CORRECT - considers viewport + DPR -->
<img
  src="/image-800.jpg"
  srcset="
    /image-400.jpg 400w,
    /image-800.jpg 800w,
    /image-1200.jpg 1200w
  "
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Image"
  width="800"
  height="600"
/>
```

**Exception**: Density descriptors are appropriate for fixed-size images like logos.

```html
<!-- ✅ CORRECT - fixed logo size -->
<img
  src="/logo.png"
  srcset="/logo.png 1x, /logo@2x.png 2x"
  alt="Logo"
  width="150"
  height="50"
/>
```

## Always Include sizes Attribute with Width Descriptors

**Problem**: Browser defaults to `100vw`, choosing unnecessarily large images.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `srcset="... 400w, ... 800w"` (no sizes) | Add `sizes="..."` |

```html
<!-- ❌ WRONG - browser assumes 100vw -->
<img
  src="/image-800.jpg"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
  alt="Image"
/>

<!-- ✅ CORRECT - specifies display size -->
<img
  src="/image-800.jpg"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Image"
  width="800"
  height="600"
/>
```

## Use Modern Formats (AVIF, WebP) with Fallbacks

**Problem**: Serving only JPEG/PNG wastes 50-70% potential bandwidth savings.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<img src="/image.jpg">` | `<picture>` with AVIF → WebP → JPEG |

```html
<!-- ❌ WRONG - missing modern formats -->
<img src="/image.jpg" alt="Image" />

<!-- ✅ CORRECT - AVIF → WebP → JPEG fallback -->
<picture>
  <source
    srcset="
      /image-400.avif 400w,
      /image-800.avif 800w,
      /image-1200.avif 1200w
    "
    sizes="(max-width: 768px) 100vw, 800px"
    type="image/avif"
  />
  <source
    srcset="
      /image-400.webp 400w,
      /image-800.webp 800w,
      /image-1200.webp 1200w
    "
    sizes="(max-width: 768px) 100vw, 800px"
    type="image/webp"
  />
  <img
    src="/image-800.jpg"
    srcset="
      /image-400.jpg 400w,
      /image-800.jpg 800w,
      /image-1200.jpg 1200w
    "
    sizes="(max-width: 768px) 100vw, 800px"
    alt="Image"
    width="800"
    height="600"
    loading="lazy"
  />
</picture>
```

## Use object-fit: cover for Fixed Aspect Ratio Containers

**Problem**: Image stretches or squashes when container size differs from image dimensions.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| No object-fit with aspect-ratio | `object-cover` or `object-contain` |

```html
<!-- ❌ WRONG - image distorts -->
<div class="w-full h-64">
  <img src="/image.jpg" alt="Image" class="w-full h-full" />
</div>

<!-- ✅ CORRECT - maintains aspect ratio, crops edges -->
<div class="w-full h-64">
  <img
    src="/image.jpg"
    alt="Image"
    class="w-full h-full object-cover"
  />
</div>

<!-- ✅ CORRECT - maintains aspect ratio, shows all content -->
<div class="w-full h-64">
  <img
    src="/logo.svg"
    alt="Logo"
    class="w-full h-full object-contain"
  />
</div>
```

## Use Correct Source Order in picture Element

**Problem**: Browser picks first matching source, wrong order serves suboptimal format.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| JPEG before WebP | AVIF → WebP → JPEG |
| Missing type attribute | Always include `type="image/..."` |

```html
<!-- ❌ WRONG - JPEG before WebP -->
<picture>
  <source srcset="/image.jpg" type="image/jpeg" />
  <source srcset="/image.webp" type="image/webp" />
  <img src="/image.jpg" alt="Image" />
</picture>

<!-- ✅ CORRECT - best to worst -->
<picture>
  <source srcset="/image.avif" type="image/avif" />
  <source srcset="/image.webp" type="image/webp" />
  <img src="/image.jpg" alt="Image" width="800" height="600" />
</picture>
```

## Use Art Direction (picture) for Different Crops

**Problem**: Same crop doesn't work well at all viewport sizes.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Same image at all sizes | Different crops via `<picture>` |
| CSS-only cropping | Server-side cropped images |

```html
<!-- ❌ WRONG - portrait crop stretched wide on desktop -->
<img
  src="/portrait.jpg"
  srcset="/portrait-400.jpg 400w, /portrait-800.jpg 800w"
  sizes="100vw"
  alt="Image"
/>

<!-- ✅ CORRECT - portrait on mobile, landscape on desktop -->
<picture>
  <source
    media="(max-width: 640px)"
    srcset="/image-portrait-400.jpg 400w, /image-portrait-800.jpg 800w"
    sizes="100vw"
  />
  <img
    src="/image-landscape-1200.jpg"
    srcset="/image-landscape-800.jpg 800w, /image-landscape-1200.jpg 1200w"
    sizes="(max-width: 1024px) 90vw, 1200px"
    alt="Image"
    width="1200"
    height="675"
    loading="lazy"
  />
</picture>
```

## Applies To

- `**/*.html`
- `**/*.tsx`, `**/*.jsx` (React components)
- `**/*.vue`, `**/*.svelte` (other frameworks)
- Any file with `<img>` or `<picture>` elements

## Testing Commands

```bash
# Check for missing width/height
grep -r '<img' --include="*.html" --include="*.tsx" | grep -v 'width=' | grep -v 'height='

# Check for missing alt
grep -r '<img' --include="*.html" --include="*.tsx" | grep -v 'alt='

# Check for missing loading attribute
grep -r '<img' --include="*.html" --include="*.tsx" | grep -v 'loading='

# Run Lighthouse audit
npx lighthouse https://example.com --only-categories=performance --view
```

## Quick Wins

1. **Add width/height to all images** - Prevents CLS
2. **Add loading="lazy" to below-fold images** - Reduces initial load
3. **Add fetchpriority="high" to hero image** - Improves LCP
4. **Generate WebP versions** - 40-50% size savings
5. **Add srcset for images >400px** - Optimize for mobile

## References

- [Web.dev: Optimize Images](https://web.dev/articles/optimize-images)
- [Web.dev: Responsive Images](https://web.dev/articles/responsive-images)
- [Web.dev: Lazy Loading](https://web.dev/articles/browser-level-image-lazy-loading)
- [Web.dev: Optimize CLS](https://web.dev/articles/optimize-cls)
- [Web.dev: Optimize LCP](https://web.dev/articles/optimize-lcp)
