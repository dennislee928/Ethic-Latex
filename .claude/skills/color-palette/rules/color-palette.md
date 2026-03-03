# Color Palette Correction Rules

Common mistakes when generating or using color palettes, and how to fix them.

---

## Never Use Raw Tailwind Colors

Use semantic tokens instead of raw Tailwind color classes.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `bg-blue-500` | `bg-primary` |
| `text-gray-600` | `text-muted-foreground` |
| `border-slate-200` | `border-border` |
| `bg-green-600` (for success) | Define `--color-success` semantic token |

**Why**: Raw colors break when switching themes, don't adapt to dark mode, and aren't brand-aligned.

**Fix pattern**:
```css
/* Don't hardcode Tailwind colors */
.button { background: #3B82F6; }

/* Use semantic tokens */
.button { background: hsl(var(--color-primary)); }
```

---

## Always Pair Background with Foreground

Every background token must have a paired foreground token.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `--color-card` only | `--color-card` + `--color-card-foreground` |
| `bg-primary` with `text-secondary` | `bg-primary` with `text-primary-foreground` |
| Changing background without foreground | Update both in dark mode |

**Why**: Dark mode breaks if foreground doesn't update with background.

**Example failure**:
```css
:root {
  --color-card: #FFFFFF;
  --color-card-foreground: #1E293B; /* Dark text */
}

.dark {
  --color-card: #1E293B; /* Now dark background */
  /* BUG: card-foreground still #1E293B - invisible text! */
}
```

**Fix**:
```css
.dark {
  --color-card: #1E293B;
  --color-card-foreground: #F1F5F9; /* Light text on dark background */
}
```

---

## Always Check Contrast for Text on Primary

Primary button text must meet WCAG AA (4.5:1 for normal text).

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| White text on primary-500 (3.9:1) | White text on primary-600 or darker |
| primary-600 text on white (5.7:1) | primary-700+ for AAA (7:1+) |
| Assuming brand color works for text | Calculate contrast ratio first |

**Quick fix**: If primary button fails contrast, use shade 100-200 darker.

```css
/* Fails AA (3.9:1) */
--color-primary: var(--color-primary-500);
--color-primary-foreground: #FFFFFF;

/* Passes AA (5.7:1) */
--color-primary: var(--color-primary-600);
--color-primary-foreground: #FFFFFF;
```

---

## Always Provide Dark Mode Variants

All color definitions need dark mode overrides.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Light mode colors only | Light mode + `.dark` overrides |
| Same shades for light and dark | Inverted shades (50↔950, 100↔900) |
| Primary-600 in both modes | Primary-600 (light), Primary-500 (dark) |

**Pattern**:
```css
@theme {
  /* Light mode */
  --color-background: #FFFFFF;
  --color-foreground: var(--color-primary-950);
  --color-primary: var(--color-primary-600);
}

.dark {
  /* Dark mode - inverted */
  --color-background: var(--color-primary-950);
  --color-foreground: var(--color-primary-50);
  --color-primary: var(--color-primary-500); /* Brighter for visibility */
}
```

---

## Use HSL for Generated Shades

HSL provides better interpolation than RGB/Hex for shade generation.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Hex interpolation (manual averaging) | Convert to HSL, vary lightness |
| RGB mixing | HSL with constant hue |
| Random lightness values | Standard scale (97%, 94%, 87%...) |

**Why**: HSL preserves hue and saturation, creating a cohesive scale. RGB mixing shifts hue unpredictably.

**Example**:
```javascript
// Don't mix hex values
const shade100 = averageHex('#0D9488', '#FFFFFF'); // ❌ Hue shifts

// Use HSL with fixed hue
const brand = { h: 174, s: 84, l: 40 }; // #0D9488
const shade100 = { h: 174, s: 67, l: 94 }; // ✅ Same hue, lighter
```

---

## Don't Use Pure Black or Pure White

Off-black and off-white look better and support elevation.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `--color-background: #000000` | `--color-background: var(--color-primary-950)` |
| `--color-foreground: #FFFFFF` | `--color-foreground: var(--color-primary-50)` |
| Pure black for dark mode | Shade 950 (10% lightness) |

**Why**:
- Pure black shows OLED smearing
- Pure white is harsh on eyes
- No room for elevation hierarchy

---

## Generate All 11 Shades

Don't skip shades in the scale - all 11 are needed for flexibility.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| 5-shade scale (100, 300, 500, 700, 900) | Full 11-shade scale (50-950) |
| Custom lightness values | Standard values (97%, 94%, 87%...) |
| Skipping 50 or 950 | Include extremes for backgrounds/text |

**Why**: UI components need full range:
- 50-300: Backgrounds, hover states
- 400-600: Brand colors, primary actions
- 700-950: Text, dark mode backgrounds

---

## Keep Hue Constant Across Shades

All shades should have the same hue value (H in HSL).

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Shifting hue for lighter shades | Constant hue, vary lightness only |
| "Warmer" lights, "cooler" darks | Same hue throughout |

**Why**: Hue shifts create disjointed palettes that don't feel like one color family.

**Example**:
```css
/* ❌ Wrong - hue shifts */
--color-primary-50: hsl(180, 70%, 97%);  /* Shifted to blue-green */
--color-primary-600: hsl(174, 84%, 40%); /* Original teal */

/* ✅ Correct - constant hue */
--color-primary-50: hsl(174, 67%, 97%);  /* Same 174deg hue */
--color-primary-600: hsl(174, 84%, 40%);
```

---

## Reduce Saturation for Light Shades

Lighter shades (50-200) should have reduced saturation to avoid garish pastels.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Full saturation for shade 50 | Reduce by 15-20% |
| Same saturation for all shades | Gradient: less for lights, full for darks |

**Pattern**:
```javascript
const baseSaturation = 84; // Brand color saturation

// Shade 50 (97% lightness)
const shade50Saturation = baseSaturation * 0.8; // 67%

// Shade 600 (40% lightness)
const shade600Saturation = baseSaturation; // 84% (full)
```

---

## Don't Override Semantic Tokens in Components

Semantic tokens should be defined globally, not overridden per component.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `.card { --color-primary: #123456; }` | Use a different semantic token |
| Component-specific color overrides | Global semantic tokens |

**Why**: Overrides break theme consistency and make dark mode unpredictable.

**Fix**: If component needs different color, define new semantic token:
```css
@theme {
  --color-primary: var(--color-primary-600);
  --color-accent: var(--color-accent-500); /* For special components */
}
```

---

## Test Dark Mode Before Finalizing

Always verify dark mode works before committing colors.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Testing light mode only | Test both light and dark modes |
| Assuming inversion works | Manually verify each token pair |

**Checklist**:
- [ ] Toggle dark mode and visually inspect
- [ ] Check text readability (no eye strain)
- [ ] Verify buttons/CTAs stand out
- [ ] Test focus rings are visible
- [ ] Check borders aren't too harsh or invisible
- [ ] Verify contrast ratios (WebAIM tool)

---

## Use Semantic Names, Not Descriptive

Token names should describe purpose, not appearance.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `--color-light-gray` | `--color-muted` |
| `--color-dark-teal` | `--color-primary` |
| `--color-bright-blue` | `--color-accent` |

**Why**: Descriptive names break when theme changes (dark mode makes "light-gray" dark).

---

## Don't Mix Color Systems

Use one color system consistently (HSL recommended for Tailwind v4).

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Mix of hex, RGB, HSL | HSL for all custom colors |
| `oklch()` for some, `hsl()` for others | Pick one system |

**Recommendation**: Use HSL for:
- Better human readability
- Easier shade generation
- Tailwind v4 compatibility

**Exception**: Use `oklch()` if perceptual uniformity is critical (advanced use cases).

---

## Summary of Rules

1. ✅ Use semantic tokens, not raw Tailwind colors
2. ✅ Pair every background with a foreground
3. ✅ Check contrast ratios (4.5:1 for text)
4. ✅ Provide dark mode overrides
5. ✅ Use HSL for shade generation
6. ✅ Avoid pure black/white
7. ✅ Generate all 11 shades (50-950)
8. ✅ Keep hue constant across shades
9. ✅ Reduce saturation for light shades
10. ✅ Test dark mode before finalizing

**Prioritize accessibility and consistency over brand purity.**
