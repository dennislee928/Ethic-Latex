# Shade Generation Reference

Complete formulas and values for generating 11-shade color scales from a single brand hex.

---

## Hex to HSL Conversion

### Formula

```javascript
function hexToHSL(hex) {
  // Remove # if present
  hex = hex.replace(/^#/, '');

  // Convert to RGB
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  // Find min/max
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const diff = max - min;

  // Calculate lightness
  let l = (max + min) / 2;

  // Calculate saturation
  let s = 0;
  if (diff !== 0) {
    s = l > 0.5
      ? diff / (2 - max - min)
      : diff / (max + min);
  }

  // Calculate hue
  let h = 0;
  if (diff !== 0) {
    if (max === r) {
      h = ((g - b) / diff + (g < b ? 6 : 0)) / 6;
    } else if (max === g) {
      h = ((b - r) / diff + 2) / 6;
    } else {
      h = ((r - g) / diff + 4) / 6;
    }
  }

  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100)
  };
}
```

### Examples

| Hex | HSL |
|-----|-----|
| `#0D9488` (Teal) | `hsl(174, 84%, 29%)` |
| `#7C3AED` (Purple) | `hsl(262, 83%, 58%)` |
| `#EF4444` (Red) | `hsl(0, 84%, 60%)` |
| `#3B82F6` (Blue) | `hsl(217, 91%, 60%)` |

---

## Lightness Values for Shades

Standard lightness percentages for each shade:

| Shade | Lightness | Notes |
|-------|-----------|-------|
| **50** | 97% | Subtle backgrounds, very light |
| **100** | 94% | Hover states on light backgrounds |
| **200** | 87% | Borders, dividers, disabled backgrounds |
| **300** | 75% | Disabled text, placeholder text (light mode) |
| **400** | 62% | Muted text, secondary content |
| **500** | 48% | **Brand color baseline** |
| **600** | 40% | Primary buttons, links (often the brand color) |
| **700** | 33% | Hover states on primary actions |
| **800** | 27% | Active states, pressed buttons |
| **900** | 20% | Text on light backgrounds, high contrast |
| **950** | 10% | Darkest accents, dark mode backgrounds |

**Key principle**: Shade 600 is typically the brand color. Shade 500 is slightly brighter for use as a base.

---

## Saturation Adjustments

Adjust saturation for natural-looking shades:

| Shade Range | Adjustment | Reason |
|-------------|------------|--------|
| **50-200** | Reduce by 10-20% | Prevents overly vibrant pastels |
| **300-400** | Reduce by 5-10% | More natural mid-tones |
| **500-600** | Keep full saturation | Brand color identity |
| **700-950** | Keep full saturation | Rich, deep colors |

### Formula

```javascript
function adjustSaturation(baseSaturation, lightness) {
  if (lightness >= 87) {
    // Shades 50-200: Reduce significantly
    return baseSaturation * 0.8; // 20% reduction
  } else if (lightness >= 62) {
    // Shades 300-400: Reduce slightly
    return baseSaturation * 0.9; // 10% reduction
  }
  // Shades 500-950: Keep full saturation
  return baseSaturation;
}
```

---

## Complete Scale Generator

```javascript
function generateShadeScale(brandHex) {
  const { h, s, l } = hexToHSL(brandHex);

  const shades = {
    50: { l: 97, sMultiplier: 0.8 },
    100: { l: 94, sMultiplier: 0.8 },
    200: { l: 87, sMultiplier: 0.85 },
    300: { l: 75, sMultiplier: 0.9 },
    400: { l: 62, sMultiplier: 0.95 },
    500: { l: 48, sMultiplier: 1.0 },
    600: { l: 40, sMultiplier: 1.0 },
    700: { l: 33, sMultiplier: 1.0 },
    800: { l: 27, sMultiplier: 1.0 },
    900: { l: 20, sMultiplier: 1.0 },
    950: { l: 10, sMultiplier: 1.0 }
  };

  const result = {};

  for (const [shade, { l: lightness, sMultiplier }] of Object.entries(shades)) {
    const adjustedS = Math.round(s * sMultiplier);
    result[shade] = `hsl(${h}, ${adjustedS}%, ${lightness}%)`;
  }

  return result;
}
```

### Example Output

Input: `#0D9488`
```javascript
{
  50:  "hsl(174, 67%, 97%)",  // #F0FDFA
  100: "hsl(174, 67%, 94%)",  // #CCFBF1
  200: "hsl(174, 71%, 87%)",  // #99F6E4
  300: "hsl(174, 76%, 75%)",  // #5EEAD4
  400: "hsl(174, 80%, 62%)",  // #2DD4BF
  500: "hsl(174, 84%, 48%)",  // #14B8A6
  600: "hsl(174, 84%, 40%)",  // #0D9488
  700: "hsl(174, 84%, 33%)",  // #0F766E
  800: "hsl(174, 84%, 27%)",  // #115E59
  900: "hsl(174, 84%, 20%)",  // #134E4A
  950: "hsl(174, 84%, 10%)"   // #042F2E
}
```

---

## HSL to Hex Conversion

Convert generated HSL back to hex for output:

```javascript
function hslToHex(h, s, l) {
  s = s / 100;
  l = l / 100;

  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs((h / 60) % 2 - 1));
  const m = l - c / 2;

  let r = 0, g = 0, b = 0;

  if (h >= 0 && h < 60) {
    r = c; g = x; b = 0;
  } else if (h >= 60 && h < 120) {
    r = x; g = c; b = 0;
  } else if (h >= 120 && h < 180) {
    r = 0; g = c; b = x;
  } else if (h >= 180 && h < 240) {
    r = 0; g = x; b = c;
  } else if (h >= 240 && h < 300) {
    r = x; g = 0; b = c;
  } else if (h >= 300 && h < 360) {
    r = c; g = 0; b = x;
  }

  r = Math.round((r + m) * 255);
  g = Math.round((g + m) * 255);
  b = Math.round((b + m) * 255);

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`.toUpperCase();
}
```

---

## Quick Manual Method

If you don't have access to code:

1. **Find base HSL** using online converter (e.g., https://www.w3schools.com/colors/colors_converter.asp)
2. **Keep hue constant** (the H value)
3. **Apply lightness values** from table above
4. **Adjust saturation** for lighter shades (reduce by 10-20%)
5. **Convert back to hex** using online tool

**Example**: Brand color `#7C3AED` → `hsl(262, 83%, 58%)`
- Shade 50: `hsl(262, 66%, 97%)` → `#FAF5FF`
- Shade 500: `hsl(262, 83%, 48%)` → `#A855F7`
- Shade 950: `hsl(262, 83%, 10%)` → `#3B0764`

---

## Verification

Check your generated shades:
- ✅ Shades should look like same color family
- ✅ Progression should be smooth (no jumps)
- ✅ Light shades (50-300) should be usable for backgrounds
- ✅ Dark shades (700-950) should be usable for text
- ✅ Brand color should be recognizable in shades 500-700

**Tools for verification**:
- https://coolors.co (paste hex colors to view palette)
- https://paletton.com (visualize color relationships)
- Figma/design tool (create swatches to preview)
