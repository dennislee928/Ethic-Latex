# Aspect Ratio and Layout Shift Prevention

## The Problem: Cumulative Layout Shift (CLS)

When images load without reserved space, content below shifts down, causing poor user experience and hurting Core Web Vitals scores.

**Visual Example:**
```
Before image loads:    After image loads:
┌─────────────────┐    ┌─────────────────┐
│ Heading         │    │ Heading         │
│ [loading...]    │    │ ╔═══════════════╗
│ Paragraph text  │    │ ║   Image       ║
└─────────────────┘    │ ║   Loaded      ║
                       │ ╚═══════════════╝
                       │ Paragraph text  │ ← Shifted down!
                       └─────────────────┘
```

## Solution 1: Explicit Width and Height (Recommended)

Always include `width` and `height` attributes. Browsers use these to calculate aspect ratio and reserve space.

### Basic Pattern

```html
<img
  src="/image.jpg"
  alt="Image"
  width="800"
  height="600"
  loading="lazy"
/>
```

**Browser calculates**: `aspect-ratio: 800 / 600` → `4:3`

### With srcset (Responsive)

```html
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

**Key Insight**: Width/height don't constrain the image size - they only set the aspect ratio. CSS can still make the image responsive.

### CSS for Responsive Sizing

```css
img {
  max-width: 100%;
  height: auto;
}
```

Or in Tailwind:

```html
<img
  src="/image.jpg"
  alt="Image"
  width="800"
  height="600"
  class="w-full h-auto"
/>
```

## Solution 2: CSS aspect-ratio Property

Use CSS `aspect-ratio` when dimensions aren't known or for container-based layouts.

### Basic Container

```html
<div class="aspect-[16/9]">
  <img
    src="/video-thumbnail.jpg"
    alt="Video thumbnail"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</div>
```

### With Tailwind v4

```html
<!-- 16:9 aspect ratio -->
<div class="aspect-[16/9]">
  <img src="/image.jpg" alt="Image" class="w-full h-full object-cover" />
</div>

<!-- 4:3 aspect ratio -->
<div class="aspect-[4/3]">
  <img src="/image.jpg" alt="Image" class="w-full h-full object-cover" />
</div>

<!-- Square (1:1) -->
<div class="aspect-square">
  <img src="/image.jpg" alt="Image" class="w-full h-full object-cover" />
</div>
```

### Custom Ratios

```css
/* 21:9 ultrawide */
.aspect-ultrawide {
  aspect-ratio: 21 / 9;
}

/* 3:2 (DSLR photos) */
.aspect-photo {
  aspect-ratio: 3 / 2;
}

/* 9:16 (vertical video) */
.aspect-portrait {
  aspect-ratio: 9 / 16;
}
```

## Common Aspect Ratios

| Ratio | CSS | Use Case |
|-------|-----|----------|
| **16:9** | `aspect-[16/9]` | Video thumbnails, hero images, modern displays |
| **4:3** | `aspect-[4/3]` | Standard photos, older displays |
| **3:2** | `aspect-[3/2]` | DSLR photos, 35mm film |
| **1:1** | `aspect-square` | Profile pictures, Instagram-style |
| **21:9** | `aspect-[21/9]` | Ultrawide banners, cinematic |
| **2:3** | `aspect-[2/3]` | Portrait photos, book covers |
| **9:16** | `aspect-[9/16]` | Vertical video (TikTok, Stories) |

## object-fit Property

Control how images fill their container while maintaining aspect ratio.

### object-fit Values

```html
<!-- Cover: Fill container, crop edges if needed -->
<img src="/image.jpg" alt="Image" class="w-full h-full object-cover" />

<!-- Contain: Fit inside container, show all content -->
<img src="/image.jpg" alt="Image" class="w-full h-full object-contain" />

<!-- Fill: Stretch to fill (avoid unless necessary) -->
<img src="/image.jpg" alt="Image" class="w-full h-full object-fill" />

<!-- Scale-down: Smaller of contain or original size -->
<img src="/image.jpg" alt="Image" class="w-full h-full object-scale-down" />

<!-- None: Original size, centered -->
<img src="/image.jpg" alt="Image" class="w-full h-full object-none" />
```

### Visual Comparison

```
Container: 400x300 (4:3)
Image: 600x400 (3:2)

object-cover (crop edges):
┌────────────────────┐
│████████████████████│
│████████████████████│
│████████████████████│
└────────────────────┘

object-contain (letterbox):
┌────────────────────┐
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Black bars
│████████████████████│
│████████████████████│
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Black bars
└────────────────────┘

object-fill (distort):
┌────────────────────┐
│█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓│ ← Stretched
│█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓│
│█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓│
└────────────────────┘
```

### When to Use Each

| Use Case | object-fit | Reasoning |
|----------|------------|-----------|
| Card images | `cover` | Fill space, crop unimportant edges |
| Product photos | `contain` | Show entire product |
| Profile pictures | `cover` | Fill circle/square, crop edges |
| Logos | `contain` | Show entire logo, preserve aspect |
| Hero backgrounds | `cover` | Fill viewport, no gaps |
| Gallery thumbnails | `cover` | Consistent grid, crop if needed |
| Document previews | `contain` | Show full page |

## object-position Property

Control which part of the image is visible when cropped with `object-cover`.

### Basic Positions

```html
<!-- Center (default) -->
<img src="/image.jpg" alt="Image" class="object-cover object-center" />

<!-- Top -->
<img src="/image.jpg" alt="Image" class="object-cover object-top" />

<!-- Bottom -->
<img src="/image.jpg" alt="Image" class="object-cover object-bottom" />

<!-- Left -->
<img src="/image.jpg" alt="Image" class="object-cover object-left" />

<!-- Right -->
<img src="/image.jpg" alt="Image" class="object-cover object-right" />
```

### Corner Positions

```html
<!-- Top-left -->
<img src="/image.jpg" alt="Image" class="object-cover object-left-top" />

<!-- Top-right -->
<img src="/image.jpg" alt="Image" class="object-cover object-right-top" />

<!-- Bottom-left -->
<img src="/image.jpg" alt="Image" class="object-cover object-left-bottom" />

<!-- Bottom-right -->
<img src="/image.jpg" alt="Image" class="object-cover object-right-bottom" />
```

### Custom Position

```css
/* Custom object position */
.object-custom {
  object-position: 70% 30%;
}
```

```html
<img
  src="/portrait.jpg"
  alt="Portrait"
  class="object-cover object-custom"
  style="object-position: 70% 30%"
/>
```

### Use Cases

| Scenario | Position | Why |
|----------|----------|-----|
| **Portrait faces** | `object-top` | Keep face visible when cropped |
| **Person walking** | `object-left` or `object-right` | Keep person in frame |
| **Landscape** | `object-center` | Balance composition |
| **Logo in corner** | `object-left-top` | Keep branding visible |
| **Action at bottom** | `object-bottom` | Keep important content |

## Complete Pattern Examples

### Card with Fixed Aspect Ratio

```html
<div class="overflow-hidden rounded-lg">
  <div class="aspect-[16/9]">
    <img
      src="/card-image-800.jpg"
      srcset="
        /card-image-400.jpg 400w,
        /card-image-800.jpg 800w,
        /card-image-1200.jpg 1200w
      "
      sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
      alt="Card image"
      width="800"
      height="450"
      loading="lazy"
      class="w-full h-full object-cover"
    />
  </div>
  <div class="p-4">
    <h3>Card Title</h3>
    <p>Card content...</p>
  </div>
</div>
```

### Profile Picture (Circle)

```html
<div class="w-32 h-32 rounded-full overflow-hidden">
  <img
    src="/profile.jpg"
    alt="Profile picture"
    width="128"
    height="128"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</div>
```

### Hero with Aspect Ratio Container

```html
<div class="aspect-[21/9] relative">
  <img
    src="/hero-1600.jpg"
    srcset="
      /hero-800.jpg 800w,
      /hero-1200.jpg 1200w,
      /hero-1600.jpg 1600w,
      /hero-2400.jpg 2400w
    "
    sizes="100vw"
    alt="Hero image"
    width="2400"
    height="1028"
    loading="eager"
    fetchpriority="high"
    class="w-full h-full object-cover"
  />
  <div class="absolute inset-0 flex items-center justify-center">
    <h1 class="text-white text-5xl font-bold">Hero Title</h1>
  </div>
</div>
```

### Gallery Grid with Consistent Sizes

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="aspect-square overflow-hidden rounded">
    <img
      src="/gallery-1.jpg"
      alt="Gallery image 1"
      width="600"
      height="600"
      loading="lazy"
      class="w-full h-full object-cover"
    />
  </div>
  <div class="aspect-square overflow-hidden rounded">
    <img
      src="/gallery-2.jpg"
      alt="Gallery image 2"
      width="600"
      height="600"
      loading="lazy"
      class="w-full h-full object-cover"
    />
  </div>
  <!-- More items... -->
</div>
```

## Browser Support

### aspect-ratio Property

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome 88+ | ✅ | Full support |
| Firefox 89+ | ✅ | Full support |
| Safari 15+ | ✅ | Full support |
| Edge 88+ | ✅ | Full support |

**Coverage**: ~95% of users (2024)

**Fallback**: Use padding-bottom hack for older browsers:

```css
/* Fallback for old browsers */
.aspect-16-9-fallback {
  position: relative;
  padding-bottom: 56.25%; /* 9/16 = 0.5625 */
}

.aspect-16-9-fallback img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

### object-fit Property

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome 32+ | ✅ | Full support |
| Firefox 36+ | ✅ | Full support |
| Safari 10+ | ✅ | Full support |
| Edge 16+ | ✅ | Full support |

**Coverage**: ~98% of users (2024)

## Common Mistakes

### ❌ Missing Width/Height

```html
<!-- Causes layout shift -->
<img src="/image.jpg" alt="Image" loading="lazy" />
```

### ❌ Inline Width Without Height

```html
<!-- Browser can't calculate aspect ratio -->
<img src="/image.jpg" alt="Image" width="800" loading="lazy" />
```

### ❌ Using max-width Without aspect-ratio

```html
<!-- Container collapses to 0 height before image loads -->
<div style="max-width: 800px">
  <img src="/image.jpg" alt="Image" loading="lazy" />
</div>
```

### ❌ object-fill Distortion

```html
<!-- Image stretches unnaturally -->
<img
  src="/portrait.jpg"
  alt="Portrait"
  class="w-full h-64 object-fill"
/>
```

### ✅ Correct Patterns

```html
<!-- Explicit dimensions -->
<img
  src="/image.jpg"
  alt="Image"
  width="800"
  height="600"
  loading="lazy"
  class="w-full h-auto"
/>

<!-- CSS aspect-ratio with object-fit -->
<div class="aspect-[16/9]">
  <img
    src="/image.jpg"
    alt="Image"
    width="1600"
    height="900"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</div>
```

## Testing for Layout Shift

### Chrome DevTools

1. Open DevTools → Performance
2. Enable "Web Vitals" in settings
3. Record page load
4. Look for "Layout Shift" markers
5. Click marker to see which elements shifted

### Lighthouse

Run Lighthouse audit:
- **CLS score**: Cumulative Layout Shift metric
- **Image elements have explicit width and height**: Checks for dimensions

### Manual Test

```javascript
// Log layout shifts
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Layout shift:', entry.value, entry.sources);
  }
}).observe({ entryTypes: ['layout-shift'] });
```

## References

- [Web.dev: Optimize CLS](https://web.dev/articles/optimize-cls)
- [MDN: aspect-ratio](https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio)
- [MDN: object-fit](https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit)
- [MDN: object-position](https://developer.mozilla.org/en-US/docs/Web/CSS/object-position)
- [CSS Tricks: Aspect Ratio Boxes](https://css-tricks.com/aspect-ratio-boxes/)
