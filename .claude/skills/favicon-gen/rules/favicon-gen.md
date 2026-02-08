# Favicon Generation Correction Rules

Rules for preventing common favicon mistakes during website development.

---

## CMS Default Favicons (CRITICAL)

Never launch a website with platform default favicons.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| "WordPress default is fine for now" | Generate custom favicon before launch |
| "We'll add favicon later" | Add favicon to pre-launch checklist (REQUIRED) |
| Skipping favicon generation | ALWAYS generate custom favicon |

### Blocked Default Icons

**NEVER use these** (instant unprofessional appearance):

- WordPress "W" icon
- Wix icon
- Squarespace icon
- Shopify bag icon
- Generic browser default (blank page icon)
- Theme placeholder icons

**Why this matters**: Default favicon signals "incomplete website" to users. First thing many notice.

---

## File Format Requirements

All six formats are required, not optional.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| "SVG only" | Generate SVG + ICO + 3 PNGs + manifest |
| "ICO is legacy, skip it" | REQUIRED for IE11/old browsers |
| "Skip manifest for simple sites" | REQUIRED for Android "Add to Home Screen" |
| "One PNG is enough" | Need 180×180 (iOS), 192×192 (Android), 512×512 (PWA) |

### Complete File Checklist

- [ ] `favicon.svg` (modern browsers, vector)
- [ ] `favicon.ico` (legacy, must have 16×16 AND 32×32)
- [ ] `apple-touch-icon.png` (180×180, solid background)
- [ ] `icon-192.png` (Android)
- [ ] `icon-512.png` (PWA)
- [ ] `site.webmanifest` (metadata)

**No exceptions**: All 6 files required for complete coverage.

---

## iOS Transparency Bug

apple-touch-icon.png MUST have solid background - transparency appears as black square.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `convert favicon.svg -resize 180x180 apple-touch-icon.png` | Add `-background "#color" -alpha remove` |
| "Transparent background is fine" | ❌ Appears as BLACK SQUARE on iOS |
| "Use same transparent PNG for all" | iOS icon needs solid, Android can be transparent |

### Correct iOS Icon Generation

```bash
# ❌ WRONG - will show black square
convert favicon.svg -resize 180x180 apple-touch-icon.png

# ✅ CORRECT - solid background
convert favicon.svg -resize 180x180 -background "#0066cc" -alpha remove apple-touch-icon.png
```

**Rule**: Always specify solid background color matching brand for iOS icons.

---

## ICO Multi-Size Requirement

favicon.ico must contain BOTH 16×16 and 32×32 sizes in one file.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `convert favicon.svg -resize 16x16 favicon.ico` | Use `-define icon:auto-resize=16,32` |
| "32×32 only" | Both sizes required (16 for tabs, 32 for retina) |
| Separate .ico files | One .ico with both sizes embedded |

### Correct ICO Generation

```bash
# ❌ WRONG - only one size
convert favicon.svg -resize 16x16 favicon.ico

# ✅ CORRECT - both sizes
convert favicon.svg -define icon:auto-resize=16,32 favicon.ico
```

**Validation**:
```bash
identify favicon.ico
# Should show TWO lines:
# favicon.ico[0] ICO 16x16
# favicon.ico[1] ICO 32x32
```

---

## Complexity at Small Sizes

Icons with too much detail become illegible at 16×16 pixels.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Using full detailed logo | Extract and simplify icon element |
| 10+ shapes in favicon | 3-5 shapes maximum |
| Gradient with 5+ stops | 2-stop gradient or solid color |
| Text below 10px | Use monogram at 14-18px bold |
| Thin lines (< 2px) | Minimum 2-3px stroke width |

### Simplification Rules

**At 16×16 pixels**:
- 1 pixel = 6.25% of canvas
- Features < 2px wide → invisible
- Gaps < 2px → merge into solid
- Details < 3×3px → illegible

**Action**: Aggressively simplify before generation.

---

## Monogram Font Weight

Text in favicons must be bold (700) weight - regular weight disappears.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `font-weight="normal"` or `font-weight="400"` | `font-weight="bold"` or `font-weight="700"` |
| No font-weight specified | ALWAYS specify bold |
| "Let font render naturally" | Force bold weight explicitly |

### Example

```xml
<!-- ❌ WRONG - letters disappear at 16x16 -->
<text x="16" y="21" font-size="18" font-family="Arial">A</text>

<!-- ✅ CORRECT - bold weight required -->
<text x="16" y="21" font-size="18" font-weight="bold" font-family="Arial">A</text>
```

---

## HTML Link Tag Order

SVG must come before ICO in HTML - order determines browser fallback priority.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| ICO link first | SVG link first (modern preferred) |
| Random link order | Specific order: SVG → ICO → Apple → Manifest |

### Correct HTML Order

```html
<!-- ✅ CORRECT ORDER -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">  <!-- 1. Modern first -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">   <!-- 2. Legacy fallback -->
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">  <!-- 3. iOS -->
<link rel="manifest" href="/site.webmanifest">  <!-- 4. Android/PWA -->

<!-- ❌ WRONG ORDER -->
<link rel="icon" href="/favicon.ico">  <!-- Legacy first = modern browsers use ICO -->
<link rel="icon" href="/favicon.svg">  <!-- Too late, already loaded ICO -->
```

**Why order matters**: Browsers use first matching `<link>` tag. SVG first ensures modern browsers get vector version.

---

## Missing Web Manifest

site.webmanifest is required for Android "Add to Home Screen" and PWAs.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| "Manifest is optional" | REQUIRED for Android home screen |
| "Only need HTML links" | Need manifest.json + HTML link |
| Skipping manifest | Generate manifest template |

### Minimum Manifest

```json
{
  "name": "Business Name",
  "short_name": "Business",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#0066cc",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

**Required fields**: name, icons (192 + 512), theme_color

---

## Cache Testing

Favicon changes require hard refresh - normal reload won't show updates.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| "Refresh page to see new favicon" | Hard refresh (Ctrl+Shift+R) |
| "Clear browser history" | Incognito/private window for testing |
| Testing immediately after upload | Wait 5-10 min for CDN propagation |

### Proper Testing Workflow

1. **Upload new favicons** to server
2. **Hard refresh** browser (Ctrl+Shift+R / Cmd+Shift+R)
3. **Test in incognito** window (no cache)
4. **Clear site data** (DevTools → Application → Clear storage)
5. **Wait 5-10 minutes** for CDN/cache propagation
6. **Test on mobile** (iOS + Android)

**Common mistake**: Testing with regular refresh, favicon still cached.

---

## File Location

Favicons must be in site root, not subdirectories (unless using absolute paths).

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `/assets/favicon.svg` | `/favicon.svg` (root) |
| `/images/icons/favicon.ico` | `/favicon.ico` (root) |
| Subdirectory without absolute path in HTML | Root location OR use `/assets/favicon.svg` absolute path |

### Correct Locations

**Vite/React**:
```
/public/
  ├── favicon.svg
  ├── favicon.ico
  ├── apple-touch-icon.png
  ├── icon-192.png
  ├── icon-512.png
  └── site.webmanifest
```

**Next.js**:
```
/public/
  ├── favicon.svg
  ├── favicon.ico
  ├── apple-touch-icon.png
  ├── icon-192.png
  ├── icon-512.png
  └── site.webmanifest
```

**Static site**:
```
/  (root)
  ├── favicon.svg
  ├── favicon.ico
  ├── apple-touch-icon.png
  ├── icon-192.png
  ├── icon-512.png
  └── site.webmanifest
```

**WordPress theme**:
```
/wp-content/themes/your-theme/
  ├── favicon.svg
  ├── favicon.ico
  ├── apple-touch-icon.png
  ├── icon-192.png
  ├── icon-512.png
  └── site.webmanifest
```

OR upload to `/wp-content/uploads/favicon/` and use absolute paths in header.php.

---

## Monogram Letter Count

Maximum 3 letters in monogram favicons - more becomes illegible.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| 4+ letter monogram | Maximum 3 letters |
| Full business name in favicon | Use initials only |
| "ACME" → "ACME" (4 letters) | "ACME" → "ACM" or "A" |

### Letter Count Guidelines

| Letters | Font Size | Readability |
|---------|-----------|-------------|
| **1** | 18-20px | ✅ Excellent |
| **2** | 14-16px | ✅ Good |
| **3** | 11-13px | ⚠️ Acceptable |
| **4+** | < 10px | ❌ Illegible |

**Rule**: 1 letter best, 2 letters good, 3 letters maximum.

---

## Contrast Requirements

Minimum 4.5:1 contrast ratio between background and foreground (WCAG AA).

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Light gray on white | Use high-contrast colors |
| Pastel on pastel | One dark, one light color |
| No contrast check | Test at https://webaim.org/resources/contrastchecker/ |

### High-Contrast Color Pairs

| Background | Foreground | Ratio | ✅/❌ |
|------------|------------|-------|------|
| #0066cc (blue) | #ffffff (white) | 6.3:1 | ✅ Good |
| #1a1a1a (dark) | #ffffff (white) | 17.9:1 | ✅ Excellent |
| #d62828 (red) | #ffffff (white) | 5.5:1 | ✅ Good |
| #cccccc (light gray) | #ffffff (white) | 1.6:1 | ❌ Fail |
| #ffff00 (yellow) | #ffffff (white) | 1.1:1 | ❌ Fail |

**Test every color pair** before finalizing.

---

## SVG Optimization

Favicons should be < 5KB for SVG - remove metadata and unnecessary attributes.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Exporting unoptimized SVG from design tool | Run through SVGO optimizer |
| SVG with comments/metadata | Strip everything except essential paths |
| Keeping all Illustrator/Figma attributes | Remove non-rendering attributes |

### SVGO Command

```bash
# Install
npm install -g svgo

# Optimize
svgo favicon.svg

# Before: 3,245 bytes → After: 892 bytes (typical)
```

**Target**: < 2KB for simple icons, < 5KB maximum.

---

## Testing Checklist

Before marking favicon task complete, verify ALL items:

### File Generation
- [ ] `favicon.svg` generated (< 5KB)
- [ ] `favicon.ico` generated with 16×16 AND 32×32
- [ ] `apple-touch-icon.png` generated (180×180, solid background)
- [ ] `icon-192.png` generated
- [ ] `icon-512.png` generated
- [ ] `site.webmanifest` created with valid JSON

### HTML Integration
- [ ] All `<link>` tags added to `<head>`
- [ ] Correct order: SVG → ICO → Apple → Manifest
- [ ] `<meta name="theme-color">` added
- [ ] File paths correct (absolute or root-relative)

### Visual Testing
- [ ] Tested at 16×16 zoom (still recognizable)
- [ ] Tested in browser tab (Chrome, Firefox, Safari)
- [ ] Tested on light AND dark browser UI
- [ ] Tested on iOS (Add to Home Screen - no black square)
- [ ] Tested on Android (Add to Home Screen - icon shows)
- [ ] Hard refresh performed (Ctrl+Shift+R)
- [ ] Tested in incognito window (no cache)

### Technical Validation
- [ ] ICO contains both 16×16 and 32×32 (`identify favicon.ico`)
- [ ] SVG is valid XML (https://validator.w3.org/)
- [ ] Manifest JSON is valid (https://manifest-validator.appspot.com/)
- [ ] All files in correct location (site root or absolute paths)
- [ ] Contrast ratio ≥ 4.5:1 (https://webaim.org/resources/contrastchecker/)

---

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "Favicon not loading" | Wrong file path or missing file | Verify file exists, check path |
| "Black square on iOS" | Transparent apple-touch-icon | Regenerate with solid background |
| "Blurry in tab" | ICO missing 16×16 size | Regenerate ICO with both sizes |
| "Android no icon" | Missing manifest or wrong icon paths | Create manifest, verify paths |
| "Favicon not updating" | Browser cache | Hard refresh, test incognito |

---

## Quick Correction Reference

**Default favicon?** → Generate custom immediately
**Transparent iOS icon?** → Add solid background
**ICO missing sizes?** → Regenerate with 16+32
**Complex icon illegible?** → Simplify to 3-5 shapes
**Text too light?** → Use bold (700) weight
**Low contrast?** → Test 4.5:1 minimum
**Missing manifest?** → Create site.webmanifest
**Wrong HTML order?** → SVG first, ICO second

---

## Applies To

- All website projects (WordPress, React, Next.js, static sites)
- Web apps and PWAs
- Any public-facing web presence
- Client websites before launch
- Personal projects (enforce professional standards)

---

**Last Updated**: 2026-01-14
**Maintained by**: Jezweb (jeremy@jezweb.net)
