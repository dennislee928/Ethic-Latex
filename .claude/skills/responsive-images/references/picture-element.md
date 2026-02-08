# Picture Element for Art Direction

## What is Art Direction?

**Art direction** means serving different **crops or compositions** of an image based on viewport size, not just scaling the same image.

### Example Use Cases

| Use Case | Mobile | Desktop | Why |
|----------|--------|---------|-----|
| **Portrait Product** | Vertical crop (portrait) | Horizontal crop (landscape) | Show product differently |
| **Hero with Text** | Tight crop, text outside | Wide shot, text overlaid | Layout changes |
| **Group Photo** | Face close-up | Full group | Show detail vs context |
| **Infographic** | Single column | Multi-column | Different layout |

### Visual Example

```
Mobile (Portrait):        Desktop (Landscape):
┌──────────┐              ┌────────────────────────┐
│          │              │                        │
│  ◉◉◉◉    │              │    ◉◉◉◉    ╔═══════╗  │
│  FACE    │              │    FACE    ║ PRODUCT║  │
│          │              │            ╚═══════╝  │
└──────────┘              └────────────────────────┘
(Tight crop)              (Full scene)
```

## Basic Syntax

```html
<picture>
  <!-- Mobile: portrait crop -->
  <source
    media="(max-width: 640px)"
    srcset="/image-portrait.jpg"
  />

  <!-- Desktop: landscape crop -->
  <source
    media="(min-width: 641px)"
    srcset="/image-landscape.jpg"
  />

  <!-- Fallback -->
  <img src="/image-landscape.jpg" alt="Image" />
</picture>
```

## Art Direction with Responsive Images

Combine `media` queries with `srcset` for both art direction AND responsive sizing.

### Pattern: Different Crops + Responsive Sizes

```html
<picture>
  <!-- Mobile: Portrait crop, multiple sizes -->
  <source
    media="(max-width: 640px)"
    srcset="
      /product-portrait-400.jpg 400w,
      /product-portrait-800.jpg 800w
    "
    sizes="100vw"
  />

  <!-- Tablet: Square crop -->
  <source
    media="(min-width: 641px) and (max-width: 1024px)"
    srcset="
      /product-square-600.jpg 600w,
      /product-square-1200.jpg 1200w
    "
    sizes="90vw"
  />

  <!-- Desktop: Landscape crop -->
  <source
    media="(min-width: 1025px)"
    srcset="
      /product-landscape-800.jpg 800w,
      /product-landscape-1200.jpg 1200w,
      /product-landscape-1600.jpg 1600w
    "
    sizes="1200px"
  />

  <!-- Fallback -->
  <img
    src="/product-landscape-1200.jpg"
    alt="Product image"
    width="1200"
    height="675"
    loading="lazy"
  />
</picture>
```

## Art Direction + Modern Formats

Combine art direction with format selection using nested sources.

### Pattern: Art Direction + WebP/AVIF

```html
<picture>
  <!-- Mobile Portrait: AVIF -->
  <source
    media="(max-width: 640px)"
    srcset="
      /hero-portrait-400.avif 400w,
      /hero-portrait-800.avif 800w
    "
    sizes="100vw"
    type="image/avif"
  />

  <!-- Mobile Portrait: WebP -->
  <source
    media="(max-width: 640px)"
    srcset="
      /hero-portrait-400.webp 400w,
      /hero-portrait-800.webp 800w
    "
    sizes="100vw"
    type="image/webp"
  />

  <!-- Mobile Portrait: JPEG -->
  <source
    media="(max-width: 640px)"
    srcset="
      /hero-portrait-400.jpg 400w,
      /hero-portrait-800.jpg 800w
    "
    sizes="100vw"
  />

  <!-- Desktop Landscape: AVIF -->
  <source
    media="(min-width: 641px)"
    srcset="
      /hero-landscape-800.avif 800w,
      /hero-landscape-1200.avif 1200w,
      /hero-landscape-1600.avif 1600w
    "
    sizes="100vw"
    type="image/avif"
  />

  <!-- Desktop Landscape: WebP -->
  <source
    media="(min-width: 641px)"
    srcset="
      /hero-landscape-800.webp 800w,
      /hero-landscape-1200.webp 1200w,
      /hero-landscape-1600.webp 1600w
    "
    sizes="100vw"
    type="image/webp"
  />

  <!-- Desktop Landscape: JPEG (fallback) -->
  <img
    src="/hero-landscape-1200.jpg"
    srcset="
      /hero-landscape-800.jpg 800w,
      /hero-landscape-1200.jpg 1200w,
      /hero-landscape-1600.jpg 1600w
    "
    sizes="100vw"
    alt="Hero image"
    width="1600"
    height="900"
    loading="eager"
    fetchpriority="high"
  />
</picture>
```

**Browser Selection Logic:**
1. Evaluate `media` queries (mobile vs desktop)
2. Within matching media query, check `type` (AVIF → WebP → JPEG)
3. Within matching type, choose size based on `srcset` + `sizes`

## Common Art Direction Patterns

### Pattern 1: Portrait vs Landscape

```html
<picture>
  <!-- Mobile: Portrait (9:16) -->
  <source
    media="(max-width: 768px)"
    srcset="/image-portrait-600.jpg"
    width="600"
    height="1066"
  />

  <!-- Desktop: Landscape (16:9) -->
  <img
    src="/image-landscape-1200.jpg"
    alt="Image"
    width="1200"
    height="675"
    loading="lazy"
  />
</picture>
```

### Pattern 2: Tight Crop vs Wide Shot

```html
<picture>
  <!-- Mobile: Face close-up -->
  <source
    media="(max-width: 640px)"
    srcset="/person-closeup-400.jpg 400w, /person-closeup-800.jpg 800w"
    sizes="100vw"
  />

  <!-- Desktop: Full scene -->
  <img
    src="/person-wide-1200.jpg"
    srcset="/person-wide-800.jpg 800w, /person-wide-1200.jpg 1200w, /person-wide-1600.jpg 1600w"
    sizes="(max-width: 1024px) 90vw, 1200px"
    alt="Person in environment"
    width="1600"
    height="900"
    loading="lazy"
  />
</picture>
```

### Pattern 3: Different Aspect Ratios

```html
<picture>
  <!-- Mobile: Square (1:1) -->
  <source
    media="(max-width: 640px)"
    srcset="/card-square-400.jpg 400w, /card-square-800.jpg 800w"
    sizes="100vw"
  />

  <!-- Tablet: 4:3 -->
  <source
    media="(min-width: 641px) and (max-width: 1024px)"
    srcset="/card-4x3-600.jpg 600w, /card-4x3-1200.jpg 1200w"
    sizes="50vw"
  />

  <!-- Desktop: 16:9 -->
  <img
    src="/card-16x9-800.jpg"
    srcset="/card-16x9-800.jpg 800w, /card-16x9-1200.jpg 1200w"
    sizes="33vw"
    alt="Card image"
    width="1200"
    height="675"
    loading="lazy"
  />
</picture>
```

### Pattern 4: Text Position Changes

```html
<picture>
  <!-- Mobile: Text below image, safe crop area -->
  <source
    media="(max-width: 768px)"
    srcset="/hero-mobile-safe-600.jpg 600w, /hero-mobile-safe-1200.jpg 1200w"
    sizes="100vw"
  />

  <!-- Desktop: Text overlaid, show full scene -->
  <img
    src="/hero-desktop-1600.jpg"
    srcset="/hero-desktop-800.jpg 800w, /hero-desktop-1200.jpg 1200w, /hero-desktop-1600.jpg 1600w"
    sizes="100vw"
    alt="Hero with headline"
    width="1600"
    height="900"
    loading="eager"
    fetchpriority="high"
  />
</picture>
```

## Media Query Breakpoints

Common breakpoints for art direction:

```html
<picture>
  <!-- Small mobile (portrait phones) -->
  <source media="(max-width: 640px)" srcset="..." />

  <!-- Tablet (portrait tablets, landscape phones) -->
  <source media="(min-width: 641px) and (max-width: 1024px)" srcset="..." />

  <!-- Desktop -->
  <img src="..." />
</picture>
```

### Alternative: min-width Only

```html
<picture>
  <!-- Desktop first -->
  <source media="(min-width: 1025px)" srcset="/image-desktop.jpg" />
  <source media="(min-width: 641px)" srcset="/image-tablet.jpg" />

  <!-- Mobile fallback -->
  <img src="/image-mobile.jpg" alt="Image" />
</picture>
```

## Orientation-Based Art Direction

Use `orientation` media feature for landscape vs portrait devices.

```html
<picture>
  <!-- Portrait orientation: Vertical crop -->
  <source
    media="(orientation: portrait)"
    srcset="/image-portrait-600.jpg 600w, /image-portrait-1200.jpg 1200w"
    sizes="100vw"
  />

  <!-- Landscape orientation: Horizontal crop -->
  <img
    src="/image-landscape-1200.jpg"
    srcset="/image-landscape-800.jpg 800w, /image-landscape-1200.jpg 1200w, /image-landscape-1600.jpg 1600w"
    sizes="100vw"
    alt="Image"
    width="1600"
    height="900"
  />
</picture>
```

### Use Cases for Orientation Queries

| Use Case | Why |
|----------|-----|
| **Video thumbnails** | Vertical video on portrait phones |
| **Splash screens** | Different hero for phone rotation |
| **Infographics** | Reflow for readability |

## Type-Based Format Selection (No Art Direction)

When you want modern formats WITHOUT art direction, use `type` only:

```html
<picture>
  <!-- Modern formats, same crop -->
  <source srcset="/image.avif" type="image/avif" />
  <source srcset="/image.webp" type="image/webp" />
  <img src="/image.jpg" alt="Image" width="800" height="600" />
</picture>
```

## Complete Real-World Example

### E-commerce Product Card

```html
<picture>
  <!-- Mobile: Portrait product, AVIF -->
  <source
    media="(max-width: 640px)"
    srcset="
      /product-portrait-300.avif 300w,
      /product-portrait-600.avif 600w
    "
    sizes="100vw"
    type="image/avif"
  />

  <!-- Mobile: Portrait product, WebP -->
  <source
    media="(max-width: 640px)"
    srcset="
      /product-portrait-300.webp 300w,
      /product-portrait-600.webp 600w
    "
    sizes="100vw"
    type="image/webp"
  />

  <!-- Mobile: Portrait product, JPEG -->
  <source
    media="(max-width: 640px)"
    srcset="
      /product-portrait-300.jpg 300w,
      /product-portrait-600.jpg 600w
    "
    sizes="100vw"
  />

  <!-- Desktop: Landscape with context, AVIF -->
  <source
    media="(min-width: 641px)"
    srcset="
      /product-landscape-400.avif 400w,
      /product-landscape-800.avif 800w,
      /product-landscape-1200.avif 1200w
    "
    sizes="(max-width: 1024px) 50vw, 33vw"
    type="image/avif"
  />

  <!-- Desktop: Landscape with context, WebP -->
  <source
    media="(min-width: 641px)"
    srcset="
      /product-landscape-400.webp 400w,
      /product-landscape-800.webp 800w,
      /product-landscape-1200.webp 1200w
    "
    sizes="(max-width: 1024px) 50vw, 33vw"
    type="image/webp"
  />

  <!-- Desktop: Landscape with context, JPEG (fallback) -->
  <img
    src="/product-landscape-800.jpg"
    srcset="
      /product-landscape-400.jpg 400w,
      /product-landscape-800.jpg 800w,
      /product-landscape-1200.jpg 1200w
    "
    sizes="(max-width: 1024px) 50vw, 33vw"
    alt="Product in lifestyle setting"
    width="1200"
    height="675"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</picture>
```

## When NOT to Use Art Direction

**Don't use art direction if:**
- Same crop works at all sizes (just use `srcset`)
- Only format conversion needed (use `type` only)
- Minor composition adjustments (CSS `object-position` may suffice)

**Example of over-engineering:**

```html
<!-- ❌ WRONG - same crop, unnecessary art direction -->
<picture>
  <source media="(max-width: 640px)" srcset="/image.jpg" />
  <source media="(min-width: 641px)" srcset="/image.jpg" />
  <img src="/image.jpg" alt="Image" />
</picture>

<!-- ✅ CORRECT - simple srcset -->
<img
  srcset="/image-400.jpg 400w, /image-800.jpg 800w, /image-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw, 800px"
  src="/image-800.jpg"
  alt="Image"
  width="800"
  height="600"
/>
```

## Testing Art Direction

### Browser DevTools

1. Open DevTools → Elements
2. Right-click `<picture>` → Inspect
3. Check which `<source>` has `currentSrc` value
4. Use Responsive Design Mode to test breakpoints
5. Network tab shows which image downloaded

### Manual Testing

```javascript
// Log which source is being used
document.querySelectorAll('picture').forEach(picture => {
  const img = picture.querySelector('img');
  console.log('Current source:', img.currentSrc);
  console.log('Natural size:', img.naturalWidth, 'x', img.naturalHeight);
});

// Listen for source changes
window.addEventListener('resize', () => {
  console.log('Window resized, source may have changed');
});
```

## Common Mistakes

### ❌ Missing Fallback img

```html
<!-- Doesn't render in browsers without picture support -->
<picture>
  <source media="(max-width: 640px)" srcset="/image-mobile.jpg" />
  <source media="(min-width: 641px)" srcset="/image-desktop.jpg" />
</picture>
```

### ❌ Wrong Media Query Logic

```html
<!-- Both sources match at 641px! -->
<picture>
  <source media="(max-width: 641px)" srcset="/mobile.jpg" />
  <source media="(min-width: 641px)" srcset="/desktop.jpg" />
  <img src="/desktop.jpg" alt="Image" />
</picture>
```

### ❌ Missing sizes in srcset Sources

```html
<!-- Browser defaults to 100vw for all sizes -->
<picture>
  <source
    media="(max-width: 640px)"
    srcset="/image-400.jpg 400w, /image-800.jpg 800w"
    <!-- Missing sizes! -->
  />
  <img src="/image-800.jpg" alt="Image" />
</picture>
```

### ❌ Type Checking Before Media Queries

```html
<!-- Wrong order: type before media -->
<picture>
  <source type="image/webp" srcset="/image-mobile.webp" />
  <source media="(max-width: 640px)" srcset="/image-mobile.jpg" />
  <img src="/image-desktop.jpg" alt="Image" />
</picture>
```

**Correct order**: `media` THEN `type` THEN size selection

### ✅ Correct Pattern

```html
<picture>
  <!-- Mobile: media → type → sizes -->
  <source
    media="(max-width: 640px)"
    srcset="/image-mobile-400.avif 400w, /image-mobile-800.avif 800w"
    sizes="100vw"
    type="image/avif"
  />
  <source
    media="(max-width: 640px)"
    srcset="/image-mobile-400.webp 400w, /image-mobile-800.webp 800w"
    sizes="100vw"
    type="image/webp"
  />
  <source
    media="(max-width: 640px)"
    srcset="/image-mobile-400.jpg 400w, /image-mobile-800.jpg 800w"
    sizes="100vw"
  />

  <!-- Desktop fallback -->
  <img
    src="/image-desktop-1200.jpg"
    srcset="/image-desktop-800.jpg 800w, /image-desktop-1200.jpg 1200w"
    sizes="(max-width: 1024px) 90vw, 1200px"
    alt="Image"
    width="1200"
    height="675"
    loading="lazy"
  />
</picture>
```

## References

- [MDN: picture element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/picture)
- [Web.dev: Art Direction](https://web.dev/articles/codelab-art-direction)
- [Responsive Images Community Group](https://responsiveimages.org/)
- [HTML Spec: picture element](https://html.spec.whatwg.org/multipage/embedded-content.html#the-picture-element)
