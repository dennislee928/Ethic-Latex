# Modern Image Formats

## Format Comparison

| Format | Quality | File Size | Transparency | Animation | Browser Support |
|--------|---------|-----------|--------------|-----------|-----------------|
| **JPEG** | Good | Medium | ❌ | ❌ | 100% |
| **PNG** | Lossless | Large | ✅ | ❌ | 100% |
| **GIF** | Limited | Medium | ✅ | ✅ | 100% |
| **WebP** | Excellent | Small | ✅ | ✅ | 97%+ |
| **AVIF** | Excellent | Smallest | ✅ | ✅ | 90%+ |

### File Size Comparison (Real Example)

**Original**: 1920×1080 photo

| Format | Quality | File Size | vs JPEG |
|--------|---------|-----------|---------|
| JPEG | 90 | 500 KB | Baseline |
| PNG-24 | Lossless | 2.1 MB | +320% |
| WebP | 90 | 250 KB | **-50%** |
| AVIF | 90 | 150 KB | **-70%** |

**Key Insight**: AVIF can be 70% smaller than JPEG at same visual quality.

## WebP Format

### Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome 32+ | ✅ | Since 2014 |
| Firefox 65+ | ✅ | Since 2019 |
| Safari 14+ | ✅ | Since Sept 2020 |
| Edge 18+ | ✅ | Full support |

**Coverage**: ~97% of users (2024)

### Basic WebP with Fallback

```html
<picture>
  <source srcset="/image.webp" type="image/webp" />
  <img src="/image.jpg" alt="Image" width="800" height="600" />
</picture>
```

### WebP with Responsive Images

```html
<picture>
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

### WebP Quality Recommendations

| Use Case | Quality | Reasoning |
|----------|---------|-----------|
| Photos | 80-90 | Excellent quality, great compression |
| UI elements | 85-95 | Sharper edges preserved |
| Thumbnails | 70-80 | Small size, acceptable quality |
| Hero images | 90-95 | Prioritize quality |

## AVIF Format

### Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome 85+ | ✅ | Since Aug 2020 |
| Firefox 93+ | ✅ | Since Oct 2021 |
| Safari 16+ | ✅ | Since Sept 2022 |
| Edge 121+ | ✅ | Since Jan 2024 |

**Coverage**: ~90% of users (2024)

### AVIF with WebP and JPEG Fallback (Recommended)

```html
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

**Browser Selection Logic:**
1. Check AVIF support → use `.avif` (smallest)
2. No AVIF, check WebP → use `.webp` (smaller)
3. No WebP → use `.jpg` (universal fallback)

### AVIF Quality Recommendations

| Use Case | Quality | Reasoning |
|----------|---------|-----------|
| Photos | 65-75 | Excellent quality, amazing compression |
| UI elements | 75-85 | Sharper edges preserved |
| Thumbnails | 50-65 | Tiny size, good quality |
| Hero images | 75-85 | Balance quality and size |

**Note**: AVIF quality scale differs from JPEG/WebP. AVIF at 70 ≈ JPEG at 90.

## Compression Quality Guidelines

### JPEG Quality Scale

| Quality | Use Case | Visual Quality | File Size |
|---------|----------|----------------|-----------|
| 60-70 | Thumbnails | Noticeable compression | Very small |
| 75-85 | Most web images | Good quality | Small |
| 85-95 | Hero images | Excellent quality | Medium |
| 95-100 | Archival | Indistinguishable from lossless | Large |

### WebP Quality Scale

| Quality | Use Case | File Size vs JPEG |
|---------|----------|-------------------|
| 70-80 | Thumbnails | -50% |
| 80-90 | Most images | -40% |
| 90-95 | Hero images | -30% |

### AVIF Quality Scale

| Quality | Use Case | File Size vs JPEG |
|---------|----------|-------------------|
| 50-65 | Thumbnails | -70% |
| 65-75 | Most images | -60% |
| 75-85 | Hero images | -50% |

## File Size Targets

Recommended maximum file sizes for web delivery:

| Image Type | Target Size | Max Size | Notes |
|------------|-------------|----------|-------|
| Hero image (1600w) | 150-250 KB | 500 KB | LCP critical |
| Content image (800w) | 80-120 KB | 200 KB | Balance quality/speed |
| Card thumbnail (600w) | 40-80 KB | 150 KB | Many per page |
| Thumbnail (300w) | 15-30 KB | 50 KB | Grid layouts |
| Icon/logo (150w) | 5-15 KB | 30 KB | Use SVG if possible |

**Over budget?** Try:
1. Lower quality (AVIF 65 vs 75)
2. Smaller dimensions (1600w → 1200w)
3. More aggressive compression
4. Convert PNG to WebP/AVIF

## Generating Modern Formats

### Using Sharp (Node.js)

```javascript
import sharp from 'sharp';

// Generate AVIF
await sharp('input.jpg')
  .avif({ quality: 70 })
  .toFile('output.avif');

// Generate WebP
await sharp('input.jpg')
  .webp({ quality: 80 })
  .toFile('output.webp');

// Generate responsive set
const widths = [400, 800, 1200, 1600];
await Promise.all(
  widths.map(width =>
    sharp('input.jpg')
      .resize(width)
      .avif({ quality: 70 })
      .toFile(`output-${width}.avif`)
  )
);
```

### Using Cloudflare Images

```typescript
// Cloudflare Images automatically serves optimal format
const imageUrl = new URL('https://imagedelivery.net/account-hash/image-id/public');

// Add format parameter (optional - auto-detects browser)
imageUrl.searchParams.set('format', 'auto'); // auto, webp, avif, json
imageUrl.searchParams.set('quality', '80');
imageUrl.searchParams.set('width', '800');

// Cloudflare serves AVIF to Chrome 85+, WebP to Safari 14+, JPEG to older browsers
```

### Using ImageMagick

```bash
# Convert to WebP
magick input.jpg -quality 80 output.webp

# Convert to AVIF
magick input.jpg -quality 70 output.avif

# Batch convert directory
for file in *.jpg; do
  magick "$file" -quality 80 "${file%.jpg}.webp"
  magick "$file" -quality 70 "${file%.jpg}.avif"
done
```

### Using cwebp (Official WebP Tool)

```bash
# Install cwebp
brew install webp  # macOS
apt install webp   # Ubuntu

# Convert to WebP
cwebp -q 80 input.jpg -o output.webp

# Lossless WebP
cwebp -lossless input.png -o output.webp

# Batch convert
for file in *.jpg; do
  cwebp -q 80 "$file" -o "${file%.jpg}.webp"
done
```

## Complete Pattern: Hero with Modern Formats

```html
<picture>
  <!-- AVIF: Best compression, modern browsers -->
  <source
    srcset="
      /hero-800.avif 800w,
      /hero-1200.avif 1200w,
      /hero-1600.avif 1600w,
      /hero-2400.avif 2400w
    "
    sizes="100vw"
    type="image/avif"
  />

  <!-- WebP: Good compression, wide support -->
  <source
    srcset="
      /hero-800.webp 800w,
      /hero-1200.webp 1200w,
      /hero-1600.webp 1600w,
      /hero-2400.webp 2400w
    "
    sizes="100vw"
    type="image/webp"
  />

  <!-- JPEG: Universal fallback -->
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
    height="1200"
    loading="eager"
    fetchpriority="high"
  />
</picture>
```

## Complete Pattern: Grid Cards with Modern Formats

```html
<picture>
  <source
    srcset="
      /card-300.avif 300w,
      /card-600.avif 600w,
      /card-900.avif 900w
    "
    sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
    type="image/avif"
  />
  <source
    srcset="
      /card-300.webp 300w,
      /card-600.webp 600w,
      /card-900.webp 900w
    "
    sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
    type="image/webp"
  />
  <img
    src="/card-600.jpg"
    srcset="
      /card-300.jpg 300w,
      /card-600.jpg 600w,
      /card-900.jpg 900w
    "
    sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
    alt="Card image"
    width="900"
    height="600"
    loading="lazy"
    class="w-full h-full object-cover"
  />
</picture>
```

## Format Selection Decision Tree

```
┌─────────────────────────────────┐
│ Need transparency or animation? │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      │ YES         │ NO
      ▼             ▼
  ┌──────────┐  ┌──────────┐
  │ PNG/GIF? │  │ Photo?   │
  └────┬─────┘  └────┬─────┘
       │             │
       │      ┌──────┴──────┐
       │      │ YES         │ NO
       │      ▼             ▼
       │  ┌────────┐    ┌──────┐
       │  │ AVIF   │    │ SVG  │
       │  │ WebP   │    │ best │
       │  │ JPEG   │    └──────┘
       │  └────────┘
       │
       ▼
  ┌───────────┐
  │ AVIF/WebP │
  │ PNG       │
  └───────────┘
```

## Common Mistakes

### ❌ Only Serving JPEG

```html
<!-- Missing 50-70% potential size savings -->
<img src="/image.jpg" alt="Image" />
```

### ❌ WebP Without JPEG Fallback

```html
<!-- Breaks in Safari < 14, older browsers -->
<img src="/image.webp" alt="Image" />
```

### ❌ Wrong Source Order

```html
<!-- Browser picks first match - JPEG before WebP! -->
<picture>
  <source srcset="/image.jpg" type="image/jpeg" />
  <source srcset="/image.webp" type="image/webp" />
  <img src="/image.jpg" alt="Image" />
</picture>
```

### ❌ Missing type Attribute

```html
<!-- Browser downloads all sources to check format -->
<picture>
  <source srcset="/image.webp" />
  <source srcset="/image.jpg" />
  <img src="/image.jpg" alt="Image" />
</picture>
```

### ✅ Correct Pattern

```html
<picture>
  <!-- Best to worst: AVIF → WebP → JPEG -->
  <source srcset="/image.avif" type="image/avif" />
  <source srcset="/image.webp" type="image/webp" />
  <img src="/image.jpg" alt="Image" width="800" height="600" />
</picture>
```

## Testing Format Support

### Feature Detection (JavaScript)

```javascript
// Check WebP support
async function supportsWebP() {
  const webp = 'data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA=';
  const blob = await fetch(webp).then(r => r.blob());
  return blob.type === 'image/webp';
}

// Check AVIF support
async function supportsAVIF() {
  const avif = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgANogQEAwgMg8f8D///8WfhwB8+ErK42A=';
  const blob = await fetch(avif).then(r => r.blob());
  return blob.type === 'image/avif';
}

// Use in code
if (await supportsAVIF()) {
  imgElement.src = '/image.avif';
} else if (await supportsWebP()) {
  imgElement.src = '/image.webp';
} else {
  imgElement.src = '/image.jpg';
}
```

### CSS Feature Detection

```css
/* WebP support */
@supports (background-image: url('test.webp')) {
  .hero {
    background-image: url('/hero.webp');
  }
}

/* AVIF support */
@supports (background-image: url('test.avif')) {
  .hero {
    background-image: url('/hero.avif');
  }
}
```

### Modernizr

```javascript
if (Modernizr.webp) {
  // Use WebP
} else {
  // Use JPEG
}
```

## Performance Impact

### Lighthouse Audit

Run Lighthouse audit to check:
- **Serve images in next-gen formats**: Flags JPEG/PNG that should be WebP/AVIF
- **Properly size images**: Checks if images are larger than needed
- **Efficiently encode images**: Flags over-compressed or inefficiently compressed

### Real Performance Gains

**Example Site**: E-commerce homepage with 20 product images

| Format | Total Size | vs JPEG | LCP Impact |
|--------|------------|---------|------------|
| JPEG (baseline) | 4.2 MB | - | 3.2s |
| WebP | 2.1 MB | **-50%** | 2.4s |
| AVIF | 1.3 MB | **-69%** | 1.8s |

**Key Insight**: Using AVIF can reduce LCP by ~1.4 seconds on mobile 3G.

## References

- [Web.dev: Use WebP Images](https://web.dev/articles/serve-images-webp)
- [Web.dev: Use AVIF Images](https://web.dev/articles/compress-images-avif)
- [caniuse: WebP](https://caniuse.com/webp)
- [caniuse: AVIF](https://caniuse.com/avif)
- [Jake Archibald: AVIF vs WebP](https://jakearchibald.com/2020/avif-has-landed/)
- [Cloudflare Images: Format Conversion](https://developers.cloudflare.com/images/transform-images/format-conversion/)
