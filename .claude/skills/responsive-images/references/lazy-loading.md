# Lazy Loading Images

## Native Lazy Loading

Modern browsers support native lazy loading via the `loading` attribute.

### Basic Usage

```html
<!-- Lazy load (most images) -->
<img src="/image.jpg" alt="Image" loading="lazy" />

<!-- Eager load (default, LCP images) -->
<img src="/hero.jpg" alt="Hero" loading="eager" />

<!-- Auto (browser decides, rarely used) -->
<img src="/image.jpg" alt="Image" loading="auto" />
```

## When to Use Eager vs Lazy

### Use loading="eager" (or omit - it's the default)

**LCP (Largest Contentful Paint) images:**
```html
<img
  src="/hero.jpg"
  alt="Hero image"
  loading="eager"
  fetchpriority="high"
/>
```

**Above-the-fold images (first screenful):**
```html
<!-- First 2-3 images visible on page load -->
<img src="/banner.jpg" alt="Banner" loading="eager" />
```

**Critical logos and branding:**
```html
<img src="/logo.svg" alt="Company Logo" loading="eager" />
```

### Use loading="lazy"

**Below-the-fold images:**
```html
<!-- Not visible until user scrolls -->
<img src="/content-image.jpg" alt="Content" loading="lazy" />
```

**Carousels and tabs:**
```html
<!-- Hidden until user interacts -->
<img src="/slide-2.jpg" alt="Slide 2" loading="lazy" />
```

**Long articles and blog posts:**
```html
<!-- Multiple images scattered throughout content -->
<img src="/article-image-5.jpg" alt="Figure 5" loading="lazy" />
```

**Grid/masonry layouts:**
```html
<!-- Many images, most below fold -->
<img src="/grid-item-20.jpg" alt="Item 20" loading="lazy" />
```

## Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome 77+ | ✅ | Full support |
| Firefox 75+ | ✅ | Full support |
| Safari 15.4+ | ✅ | Added Sept 2021 |
| Edge 79+ | ✅ | Full support |

**Coverage**: ~95% of users (2024)

**Polyfill**: Not needed - gracefully degrades to eager loading in unsupported browsers

## Loading Distance Thresholds

Browsers start loading lazy images **before they enter the viewport**. Thresholds vary:

| Browser | Distance | Notes |
|---------|----------|-------|
| Chrome | 1250px on fast connections, 2500px on slow (4G) | Adapts to network |
| Firefox | 200px | Fixed threshold |
| Safari | ~100-200px | Fixed threshold |

**Key Insight**: You don't need to micro-optimize. Browsers handle the loading distance intelligently based on connection speed.

## fetchpriority for LCP Optimization

Use `fetchpriority="high"` on LCP images to boost download priority.

### Hero Image (LCP)

```html
<img
  src="/hero-1200.jpg"
  srcset="
    /hero-800.jpg 800w,
    /hero-1200.jpg 1200w,
    /hero-1600.jpg 1600w
  "
  sizes="100vw"
  alt="Hero image"
  width="1600"
  height="900"
  loading="eager"
  fetchpriority="high"
/>
```

### When to Use fetchpriority="high"

- **LCP images**: Always
- **Above-the-fold hero images**: Yes
- **First carousel slide**: If carousel is LCP, yes
- **Logo**: Rarely needed (small files load fast anyway)

### fetchpriority Values

| Value | Meaning | Use Case |
|-------|---------|----------|
| `high` | Prioritize this resource | LCP images, critical assets |
| `low` | Deprioritize this resource | Below-fold, non-critical |
| `auto` | Browser decides (default) | Most images |

## Intersection Observer (Custom Lazy Loading)

For advanced use cases or older browser support, use Intersection Observer.

### Basic Pattern

```javascript
const imageObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove('lazy');
      observer.unobserve(img);
    }
  });
});

document.querySelectorAll('img.lazy').forEach(img => {
  imageObserver.observe(img);
});
```

### HTML

```html
<img
  data-src="/image.jpg"
  src="/placeholder.jpg"
  alt="Image"
  class="lazy"
/>
```

### When to Use Intersection Observer

- **Legacy browser support**: Safari < 15.4, older iOS
- **Custom loading distance**: Need different threshold than browser default
- **Loading animations**: Fade-in effects when images load
- **Placeholder strategies**: Blur-up, LQIP (Low Quality Image Placeholder)
- **Analytics**: Track when images enter viewport

### With Blur-Up Placeholder

```javascript
const imageObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      const fullSrc = img.dataset.src;

      // Preload full image
      const tempImg = new Image();
      tempImg.onload = () => {
        img.src = fullSrc;
        img.classList.add('loaded');
      };
      tempImg.src = fullSrc;

      observer.unobserve(img);
    }
  });
}, {
  rootMargin: '50px' // Start loading 50px before entering viewport
});
```

### CSS for Blur-Up

```css
.lazy {
  filter: blur(10px);
  transition: filter 0.3s;
}

.lazy.loaded {
  filter: blur(0);
}
```

### HTML

```html
<img
  src="/image-tiny.jpg"
  data-src="/image-full.jpg"
  alt="Image"
  class="lazy"
/>
```

## Blur Placeholder Pattern (Modern Approach)

Use CSS backdrop-filter with data URI placeholder.

### HTML

```html
<div class="image-container">
  <img
    src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600'%3E%3Cfilter id='b' color-interpolation-filters='sRGB'%3E%3CfeGaussianBlur stdDeviation='20'/%3E%3C/filter%3E%3Cimage filter='url(%23b)' x='0' y='0' height='100%25' width='100%25' href='data:image/jpeg;base64,...'/%3E%3C/svg%3E"
    data-src="/image-full.jpg"
    alt="Image"
    loading="lazy"
    class="blur-load"
  />
</div>
```

### CSS

```css
.blur-load {
  transition: filter 0.3s;
}

.blur-load[src*="data:image"] {
  filter: blur(5px);
}
```

### JavaScript

```javascript
document.querySelectorAll('.blur-load').forEach(img => {
  img.addEventListener('load', () => {
    if (img.src.startsWith('data:')) return;
    img.style.filter = 'blur(0)';
  });
});
```

## Performance Considerations

### Loading Lazy Images Too Late

**Problem**: Images load when user scrolls to them, causing blank spaces

**Solution**: Browsers already load images ~1250px before they enter viewport. Trust native lazy loading distance on fast connections.

### Loading Lazy Images Too Early

**Problem**: Loading too many images at once, wasting bandwidth

**Solution**: Use `loading="lazy"` on all below-fold images. Browser handles loading distance based on connection speed.

### LCP Delay from Lazy Loading

**Problem**: Marking LCP image as lazy delays its load

```html
<!-- ❌ WRONG - delays LCP -->
<img src="/hero.jpg" alt="Hero" loading="lazy" />
```

**Solution**: Use `loading="eager"` and `fetchpriority="high"`

```html
<!-- ✅ CORRECT -->
<img
  src="/hero.jpg"
  alt="Hero"
  loading="eager"
  fetchpriority="high"
/>
```

### Lazy Loading Above-the-Fold Images

**Problem**: Lazy loading images visible on page load

**Rule of Thumb**: First 2-3 images should be eager, rest lazy

```html
<!-- Above fold - eager -->
<img src="/banner.jpg" alt="Banner" loading="eager" />
<img src="/featured.jpg" alt="Featured" loading="eager" />

<!-- Below fold - lazy -->
<img src="/content-1.jpg" alt="Content" loading="lazy" />
<img src="/content-2.jpg" alt="Content" loading="lazy" />
```

## Testing Lazy Loading

### Chrome DevTools

1. Open DevTools → Network tab
2. Filter by "Img"
3. Throttle to "Slow 3G"
4. Reload page
5. Scroll slowly
6. Observe images loading as they approach viewport

### Lighthouse

Run Lighthouse audit:
- **Offscreen Images**: Checks if below-fold images use lazy loading
- **LCP**: Checks if LCP image is eagerly loaded

### Manual Testing

```javascript
// Check if image is lazy loaded
document.querySelectorAll('img').forEach(img => {
  console.log(img.src, img.loading);
});

// Check LCP element
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP:', lastEntry.element);
}).observe({ entryTypes: ['largest-contentful-paint'] });
```

## Common Mistakes

### ❌ Lazy Loading LCP Image

```html
<!-- Delays LCP, hurts Core Web Vitals -->
<img src="/hero.jpg" alt="Hero" loading="lazy" />
```

### ❌ Eager Loading All Images

```html
<!-- Wastes bandwidth, slows page load -->
<img src="/grid-item-20.jpg" alt="Item 20" loading="eager" />
```

### ❌ Missing fetchpriority on LCP

```html
<!-- LCP image competes with other resources -->
<img src="/hero.jpg" alt="Hero" loading="eager" />
```

### ✅ Correct Pattern

```html
<!-- LCP: eager + high priority -->
<img
  src="/hero.jpg"
  alt="Hero"
  loading="eager"
  fetchpriority="high"
/>

<!-- Above fold (not LCP): eager, no fetchpriority -->
<img src="/banner.jpg" alt="Banner" loading="eager" />

<!-- Below fold: lazy -->
<img src="/content.jpg" alt="Content" loading="lazy" />
```

## References

- [Web.dev: Browser-level lazy loading](https://web.dev/articles/browser-level-image-lazy-loading)
- [MDN: loading attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#loading)
- [MDN: fetchpriority attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#fetchpriority)
- [Web.dev: Optimize LCP](https://web.dev/articles/optimize-lcp)
- [HTML Spec: Lazy loading attribute](https://html.spec.whatwg.org/multipage/urls-and-fetching.html#lazy-loading-attributes)
