# Contrast Checking Reference

WCAG contrast ratio formulas and verification methods for accessible color palettes.

---

## WCAG Standards

### Minimum Contrast Ratios

| Content Type | AA | AAA |
|--------------|-----|-----|
| **Normal text** (<18px or <14px bold) | 4.5:1 | 7:1 |
| **Large text** (≥18px or ≥14px bold) | 3:1 | 4.5:1 |
| **UI components** (buttons, borders) | 3:1 | Not defined |
| **Graphical objects** (icons, charts) | 3:1 | Not defined |

**Target**: AA for most projects, AAA for high-accessibility needs (government, healthcare).

---

## Relative Luminance Formula

Calculate relative luminance for each color:

```javascript
function getLuminance(hex) {
  // Convert hex to RGB
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  // Apply gamma correction
  const rsRGB = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
  const gsRGB = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
  const bsRGB = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);

  // Calculate luminance
  return 0.2126 * rsRGB + 0.7152 * gsRGB + 0.0722 * bsRGB;
}
```

**Output**: Value between 0 (black) and 1 (white).

**Examples**:
- `#FFFFFF` (white) → 1.0
- `#000000` (black) → 0.0
- `#14B8A6` (teal-500) → 0.42

---

## Contrast Ratio Formula

```javascript
function getContrastRatio(hex1, hex2) {
  const lum1 = getLuminance(hex1);
  const lum2 = getLuminance(hex2);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
}
```

**Example**:
```javascript
getContrastRatio('#FFFFFF', '#0D9488'); // White text on teal-600
// → 4.56:1 (passes AA for normal text)
```

---

## Quick Check Table

Approximate contrast ratios for common shade pairs (teal palette):

### Light Mode

| Foreground | Background | Ratio | Pass AA? | Use Case |
|------------|------------|-------|----------|----------|
| 950 | white | 18.5:1 | ✅ AAA | Body text |
| 900 | white | 14.2:1 | ✅ AAA | Card text |
| 800 | white | 10.8:1 | ✅ AAA | Strong text |
| 700 | white | 8.1:1 | ✅ AAA | Text |
| 600 | white | 5.7:1 | ✅ AA | Text, buttons |
| 500 | white | 3.9:1 | ❌ Fail | Too light for text |
| 400 | white | 2.8:1 | ❌ Fail | UI only |
| white | 600 | 5.7:1 | ✅ AA | Button text |
| white | 700 | 8.1:1 | ✅ AAA | Button text |
| 600 | 50 | 5.4:1 | ✅ AA | Muted section text |

### Dark Mode

| Foreground | Background | Ratio | Pass AA? | Use Case |
|------------|------------|-------|----------|----------|
| 50 | 950 | 18.5:1 | ✅ AAA | Body text |
| 50 | 900 | 14.2:1 | ✅ AAA | Card text |
| 100 | 950 | 16.8:1 | ✅ AAA | Text |
| 400 | 950 | 8.2:1 | ✅ AAA | Muted text |
| 400 | 900 | 6.3:1 | ✅ AA | Muted text |
| white | 500 | 3.9:1 | ❌ Fail | Too bright |
| white | 600 | 5.7:1 | ✅ AA | Button text |
| white | 700 | 8.1:1 | ✅ AAA | Button text |

**Pattern**: Darker shades (700+) work for text on light backgrounds. Lighter shades (50-100) work on dark backgrounds.

---

## Common Pairs to Check

### Essential Checks

1. **Body text**: `foreground` on `background`
   - Light: 950 on white → 18.5:1 ✅
   - Dark: 50 on 950 → 18.5:1 ✅

2. **Primary button text**: `primary-foreground` on `primary`
   - Light: white on 600 → 5.7:1 ✅
   - Dark: white on 500 → 3.9:1 ⚠️ (borderline)

3. **Muted text**: `muted-foreground` on `muted`
   - Light: 600 on 50 → 5.4:1 ✅
   - Dark: 400 on 800 → 4.1:1 ❌ (fails AA)

4. **Card text**: `card-foreground` on `card`
   - Light: 900 on white → 14.2:1 ✅
   - Dark: 50 on 900 → 14.2:1 ✅

5. **Border contrast**: `border` on `background`
   - Light: 200 on white → 2.4:1 ❌ (UI only, no text)
   - Dark: 800 on 950 → 1.9:1 ❌ (subtle, acceptable for borders)

---

## Fixing Poor Contrast

### Problem: Text on Primary Button Fails

**Symptom**: White text on teal-500 = 3.9:1 (fails AA 4.5:1).

**Fix 1**: Use darker shade for primary button.
```css
/* Instead of shade 500 */
--color-primary: var(--color-primary-600); /* Darker, 5.7:1 contrast */
```

**Fix 2**: Use dark text instead of white.
```css
--color-primary-foreground: var(--color-primary-950); /* Dark text */
```

**Trade-off**: Fix 1 preserves white text (more common pattern).

---

### Problem: Muted Text Too Light

**Symptom**: primary-400 on primary-800 = 4.1:1 (fails AA 4.5:1).

**Fix**: Use more extreme shades.
```css
.dark {
  --color-muted: var(--color-primary-900); /* Darker background */
  --color-muted-foreground: var(--color-primary-300); /* Brighter text */
}
```

**Result**: 300 on 900 = 6.8:1 ✅

---

### Problem: Links Hard to See

**Symptom**: primary-500 text on white = 3.9:1 (fails AA).

**Fix 1**: Darken link color.
```css
a { color: var(--color-primary-700); } /* 8.1:1 ✅ */
```

**Fix 2**: Add underline (doesn't rely on color alone).
```css
a { text-decoration: underline; color: var(--color-primary-500); }
```

**Best practice**: Combine color + underline for accessibility.

---

## Lightness vs Contrast Quick Reference

Approximate contrast ratios by lightness difference:

| Lightness Difference | Contrast Ratio | Pass AA? |
|----------------------|----------------|----------|
| 10% → 90% | ~12:1 | ✅ AAA |
| 10% → 80% | ~9:1 | ✅ AAA |
| 10% → 70% | ~7:1 | ✅ AAA |
| 10% → 60% | ~5.5:1 | ✅ AA |
| 10% → 50% | ~4.2:1 | ❌ Borderline |
| 20% → 90% | ~9:1 | ✅ AAA |
| 30% → 90% | ~7:1 | ✅ AAA |
| 40% → 90% | ~5.5:1 | ✅ AA |
| 50% → 90% | ~4.2:1 | ❌ Borderline |

**Rule of thumb**: For text, aim for 50%+ lightness difference (e.g., 10% background + 60%+ foreground).

---

## Online Tools

Use these for quick verification:

1. **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
   - Input two hex colors
   - Shows AA/AAA pass/fail

2. **Coolors Contrast Checker**: https://coolors.co/contrast-checker
   - Visual interface
   - Suggests fixes

3. **Accessible Colors**: https://accessible-colors.com
   - Auto-generates accessible variants

4. **Browser DevTools**:
   - Chrome: Inspect element → Styles → Click color swatch → Shows contrast ratio
   - Firefox: Similar built-in checker

---

## Automated Checks

### JavaScript Function

```javascript
function checkAccessibility(foreground, background, textSize = 'normal') {
  const ratio = getContrastRatio(foreground, background);
  const minRatio = textSize === 'large' ? 3 : 4.5;

  return {
    ratio: ratio.toFixed(2),
    passAA: ratio >= minRatio,
    passAAA: ratio >= (textSize === 'large' ? 4.5 : 7),
  };
}

// Usage
const result = checkAccessibility('#0D9488', '#FFFFFF', 'normal');
console.log(result); // { ratio: "5.70", passAA: true, passAAA: false }
```

### CI/CD Integration

```javascript
// In test suite
describe('Color Palette Accessibility', () => {
  test('body text passes AA', () => {
    const ratio = getContrastRatio(
      tokens['color-foreground'],
      tokens['color-background']
    );
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  test('primary button text passes AA', () => {
    const ratio = getContrastRatio(
      tokens['color-primary-foreground'],
      tokens['color-primary']
    );
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });
});
```

---

## Edge Cases

### 1. Transparent Backgrounds

For colors with opacity, calculate against final rendered color:

```javascript
// If primary-600 at 50% opacity on white background
const foreground = '#0D9488';
const backgroundFinal = blendColors('#0D9488', '#FFFFFF', 0.5); // Helper function
const ratio = getContrastRatio('#FFFFFF', backgroundFinal);
```

### 2. Gradients

Check both endpoints:
```javascript
const gradient = 'linear-gradient(to right, #14B8A6, #0D9488)';
// Check: white text on #14B8A6 AND white text on #0D9488
```

### 3. Overlays

Text on images/videos needs high contrast (prefer 7:1+) or text shadows/backgrounds.

```css
/* Add semi-opaque background behind text */
.hero-text {
  background: rgba(0, 0, 0, 0.6);
  color: white; /* Now 7:1+ on darkened background */
}
```

---

## Verification Checklist

- [ ] Body text: ≥4.5:1 (normal) or ≥3:1 (large)
- [ ] Primary button text: ≥4.5:1
- [ ] Secondary button text: ≥4.5:1
- [ ] Muted text: ≥4.5:1
- [ ] Links: ≥4.5:1 (or underlined)
- [ ] UI elements (borders): ≥3:1
- [ ] Focus indicators: ≥3:1
- [ ] Error text: ≥4.5:1
- [ ] Dark mode: All above checks pass

**Test both modes** before shipping.

---

## Summary

1. **Calculate luminance** for each color
2. **Calculate contrast ratio** = (lighter + 0.05) / (darker + 0.05)
3. **Compare to WCAG minimums** (4.5:1 text, 3:1 UI)
4. **Fix failures** by adjusting shades (darker foreground or lighter background)
5. **Verify with online tools** (WebAIM, Coolors)
6. **Test in both light and dark modes**

**Prioritize readability over brand purity** - accessible colors build trust and expand reach.
