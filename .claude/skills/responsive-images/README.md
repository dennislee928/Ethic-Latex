# Responsive Images Skill

Implement performant responsive images with srcset, sizes, lazy loading, and modern formats (WebP, AVIF).

## Auto-Trigger Keywords

This skill should be suggested when the user mentions:

**Image Attributes:**
- srcset, sizes attribute, width descriptors
- loading="lazy", loading="eager", fetchpriority
- aspect-ratio, width, height attributes
- alt text, accessibility

**Technologies:**
- responsive images, picture element
- webp, avif, modern image formats
- lazy loading, native lazy loading
- Intersection Observer

**Performance:**
- Core Web Vitals, LCP, CLS
- layout shift, Cumulative Layout Shift
- image optimization, web performance
- fetchpriority="high"

**CSS:**
- object-fit, object-cover, object-contain
- object-position, aspect-ratio property
- aspect-[16/9], aspect-square

**Use Cases:**
- hero images, banner images
- card images, grid images
- thumbnail images, gallery images
- art direction, responsive art direction

**Error Messages:**
- "image causes layout shift"
- "poor CLS score"
- "LCP is an image"
- "Properly size images"
- "Serve images in next-gen formats"
- "Defer offscreen images"
- "Image displayed larger than intrinsic size"

## What This Skill Covers

1. **srcset and sizes attributes** - Width descriptors, responsive breakpoints, browser selection
2. **Lazy loading** - Native loading="lazy", fetchpriority, LCP optimization
3. **Modern formats** - WebP, AVIF with fallbacks using picture element
4. **Aspect ratio** - CSS aspect-ratio, explicit dimensions, CLS prevention
5. **object-fit** - Cover, contain, fill, scale-down for cropping control
6. **Art direction** - Picture element with media queries for different crops
7. **Performance** - Core Web Vitals optimization, LCP, CLS best practices

## Quick Example

```html
<img
  src="/images/hero-1200.jpg"
  srcset="
    /images/hero-800.jpg 800w,
    /images/hero-1200.jpg 1200w,
    /images/hero-1600.jpg 1600w
  "
  sizes="(max-width: 768px) 100vw, 1200px"
  alt="Hero image description"
  width="1600"
  height="900"
  loading="eager"
  fetchpriority="high"
/>
```

## Related Skills

- cloudflare-images - Cloudflare Images API integration
- cloudflare-r2 - R2 storage for image hosting
- tailwind-v4-shadcn - Tailwind classes for image styling
