# srcset and sizes Attributes

## Width Descriptors vs Density Descriptors

### Width Descriptors (w) - Recommended

Width descriptors tell the browser the **actual width of each image file** in pixels. The browser uses this with the `sizes` attribute and device pixel ratio to choose the optimal image.

```html
<img
  src="/image-800.jpg"
  srcset="
    /image-400.jpg 400w,
    /image-800.jpg 800w,
    /image-1200.jpg 1200w,
    /image-1600.jpg 1600w
  "
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Responsive image"
/>
```

**Browser Selection Logic:**
1. Calculate display width from `sizes` attribute
2. Multiply by device pixel ratio (DPR)
3. Choose smallest image ≥ calculated width
4. Consider network conditions and cache

**Example**: On a 375px wide phone (2x DPR):
- `sizes` evaluates to `375px` (100vw on mobile)
- Multiply by DPR: `375 * 2 = 750px`
- Browser chooses `image-800.jpg` (smallest ≥ 750px)

### Density Descriptors (x) - For Fixed Sizes Only

Density descriptors specify images for different device pixel ratios. Only use for **fixed-size images** like logos.

```html
<!-- Logo - fixed 150px width -->
<img
  src="/logo.png"
  srcset="/logo.png 1x, /logo@2x.png 2x, /logo@3x.png 3x"
  alt="Company logo"
  width="150"
  height="50"
/>
```

**When to Use Density Descriptors:**
- Logos and icons with fixed display size
- UI elements that don't scale with viewport
- Images where you control exact display dimensions

**Don't Use For:**
- Images that scale with viewport (use width descriptors)
- Content images in responsive layouts
- Grid or column-based images

## Common sizes Patterns

### Full-Width Images

```html
<!-- Simple full-width -->
sizes="100vw"

<!-- Full-width with max-width container -->
sizes="(max-width: 640px) 100vw,
       (max-width: 1024px) 90vw,
       1200px"
```

### Content Width Images

```html
<!-- Content area (max 800px) -->
sizes="(max-width: 768px) 100vw, 800px"

<!-- Article content (max 700px) -->
sizes="(max-width: 768px) 100vw, 700px"

<!-- With padding on mobile -->
sizes="(max-width: 640px) calc(100vw - 2rem),
       (max-width: 1024px) 90vw,
       800px"
```

### Grid Images

```html
<!-- 2-column grid (mobile full-width) -->
sizes="(max-width: 768px) 100vw, 50vw"

<!-- 3-column grid -->
sizes="(max-width: 640px) 100vw,
       (max-width: 1024px) 50vw,
       33vw"

<!-- 4-column grid with max-width -->
sizes="(max-width: 640px) 100vw,
       (max-width: 768px) 50vw,
       (max-width: 1024px) 33vw,
       25vw"

<!-- Grid with gaps (12 cols, 3-wide, 2rem gap) -->
sizes="(max-width: 768px) 100vw,
       calc((100vw - 4rem) / 3)"
```

### Sidebar Images

```html
<!-- Fixed sidebar width -->
sizes="300px"

<!-- Responsive sidebar -->
sizes="(max-width: 1024px) 100vw, 300px"
```

### Multi-Layout Images

```html
<!-- Hero on mobile, sidebar on desktop -->
sizes="(max-width: 768px) 100vw, 400px"

<!-- Full-width mobile, 2/3 width desktop -->
sizes="(max-width: 768px) 100vw, 66vw"
```

## Recommended Breakpoints

### Standard Image Sizes to Generate

| Use Case | Recommended Widths | Reasoning |
|----------|-------------------|-----------|
| **Full-width hero** | 800w, 1200w, 1600w, 2400w | Covers mobile (800), tablet (1200), desktop (1600), retina (2400) |
| **Content images** | 400w, 800w, 1200w | Covers mobile, tablet, desktop at 1x/2x DPR |
| **Grid cards (3-col)** | 300w, 600w, 900w | Covers ~33vw at 1x/2x/3x DPR |
| **Thumbnails** | 150w, 300w | Small fixed-size images at 1x/2x |
| **Sidebar images** | 300w, 600w | Fixed width at 1x/2x DPR |

### DPR Considerations

Modern devices have varying pixel densities:

| Device Type | Typical DPR | Example |
|-------------|-------------|---------|
| Standard desktop | 1x | Older monitors |
| Retina desktop | 2x | MacBook Pro, 4K monitors |
| Standard mobile | 2x | iPhone 11, Pixel 4 |
| High-end mobile | 3x | iPhone 14 Pro, Samsung S23 |

**Generate images up to 2-3x the display width** to cover high-DPR devices.

## Calculating Required Image Sizes

**Formula**: `Display Width × Max DPR = Image Width`

**Example**: Content image displayed at 800px max width
- 1x DPR: 800 × 1 = 800w
- 2x DPR: 800 × 2 = 1600w
- 3x DPR: 800 × 3 = 2400w

**Recommended sizes**: `400w, 800w, 1200w, 1600w`

## Browser Selection Examples

### Example 1: Content Image

```html
<img
  srcset="
    /content-400.jpg 400w,
    /content-800.jpg 800w,
    /content-1200.jpg 1200w
  "
  sizes="(max-width: 768px) 100vw, 800px"
/>
```

**Selection on 375px mobile (2x DPR):**
1. `sizes` evaluates to `375px` (100vw)
2. Multiply by DPR: `375 * 2 = 750px`
3. Browser chooses `content-800.jpg`

**Selection on 1920px desktop (1x DPR):**
1. `sizes` evaluates to `800px`
2. Multiply by DPR: `800 * 1 = 800px`
3. Browser chooses `content-800.jpg`

**Selection on 1920px retina desktop (2x DPR):**
1. `sizes` evaluates to `800px`
2. Multiply by DPR: `800 * 2 = 1600px`
3. Browser would prefer 1600w, but max available is 1200w
4. Browser chooses `content-1200.jpg`

### Example 2: Grid Cards (3-column)

```html
<img
  srcset="
    /card-300.jpg 300w,
    /card-600.jpg 600w,
    /card-900.jpg 900w
  "
  sizes="(max-width: 768px) 100vw, 33vw"
/>
```

**Selection on 375px mobile (2x DPR):**
1. `sizes` evaluates to `375px` (100vw on mobile)
2. Multiply by DPR: `375 * 2 = 750px`
3. Browser chooses `card-900.jpg`

**Selection on 1440px desktop (2x DPR):**
1. `sizes` evaluates to `~480px` (33vw of 1440px)
2. Multiply by DPR: `480 * 2 = 960px`
3. Browser would prefer 960w, chooses closest: `card-900.jpg`

## Tips for Writing sizes

1. **Mobile-first**: Start with mobile sizes, then add larger breakpoints
2. **Match layout breakpoints**: Use same breakpoints as your CSS
3. **Consider container width**: Account for padding, gaps, max-width
4. **Test with DevTools**: Chrome DevTools shows which image was selected
5. **Don't overthink**: Browser is smart, close approximations work fine

## Common Mistakes

### ❌ Missing sizes Attribute

```html
<!-- Browser defaults to 100vw, wastes bandwidth on small displays -->
<img
  src="/image-800.jpg"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
  alt="Image"
/>
```

### ❌ Using Density Descriptors for Responsive Images

```html
<!-- Browser can't optimize for viewport size -->
<img
  src="/image.jpg"
  srcset="/image.jpg 1x, /image@2x.jpg 2x"
  alt="Image"
/>
```

### ❌ Wrong sizes Calculation

```html
<!-- Image displays at 800px max, but sizes says 100vw -->
<img
  srcset="/image-400.jpg 400w, /image-800.jpg 800w, /image-1200.jpg 1200w"
  sizes="100vw"
  alt="Image"
  style="max-width: 800px"
/>
<!-- Browser chooses 1200w on 1200px+ viewports, wasting bandwidth -->
```

### ✅ Correct Version

```html
<img
  srcset="/image-400.jpg 400w, /image-800.jpg 800w, /image-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Image"
/>
```

## Tools for Testing

**Chrome DevTools:**
1. Right-click image → Inspect
2. Look for "currentSrc" in Elements panel
3. Network tab shows which image was downloaded

**Firefox DevTools:**
1. Right-click image → Inspect
2. Computed tab shows currentSrc
3. Responsive Design Mode to test different viewports

**Online Calculators:**
- [Responsive Image Breakpoints Generator](https://responsivebreakpoints.com/)
- [RespImageLint](https://ausi.github.io/respimagelint/) - Linter for responsive images

## References

- [MDN: Responsive Images](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images)
- [HTML Spec: srcset attribute](https://html.spec.whatwg.org/multipage/images.html#srcset-attributes)
- [Web.dev: Serve Responsive Images](https://web.dev/articles/serve-responsive-images)
