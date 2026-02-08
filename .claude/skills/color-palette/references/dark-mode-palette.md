# Dark Mode Palette Reference

Patterns for creating dark mode color palettes that preserve brand identity while ensuring readability.

---

## Inversion Pattern

Dark mode inverts lightness while preserving hue and saturation.

### Shade Mapping

| Light Mode Shade | Dark Mode Shade | Lightness Swap |
|------------------|-----------------|----------------|
| 50 (97% L) | 950 (10% L) | Backgrounds |
| 100 (94% L) | 900 (20% L) | Subtle backgrounds |
| 200 (87% L) | 800 (27% L) | Borders |
| 300 (75% L) | 700 (33% L) | Disabled states |
| 400 (62% L) | 600 (40% L) | Muted text |
| 500 (48% L) | **500 (slightly brighter)** | Brand color baseline |
| 600 (40% L) | 400 (62% L) | Primary actions |
| 700 (33% L) | 300 (75% L) | Rarely used |
| 800 (27% L) | 200 (87% L) | Rarely used |
| 900 (20% L) | 100 (94% L) | Card backgrounds |
| 950 (10% L) | 50 (97% L) | Text color |

**Key principle**: Swap extremes (50↔950), preserve middle (500 stays near 500).

---

## CSS Implementation

### Method 1: Override Variables in .dark

```css
@theme {
  /* Light mode (default) */
  --color-background: #FFFFFF;
  --color-foreground: var(--color-primary-950);
  --color-card: #FFFFFF;
  --color-card-foreground: var(--color-primary-900);
  --color-primary: var(--color-primary-600);
  --color-border: var(--color-primary-200);
}

.dark {
  /* Dark mode overrides */
  --color-background: var(--color-primary-950);
  --color-foreground: var(--color-primary-50);
  --color-card: var(--color-primary-900);
  --color-card-foreground: var(--color-primary-50);
  --color-primary: var(--color-primary-500);
  --color-border: var(--color-primary-800);
}
```

**Advantage**: Single source of truth, easy to maintain.

### Method 2: Separate Light/Dark Scale

```css
@theme {
  /* Light mode shades */
  --color-primary-50-light: #F0FDFA;
  --color-primary-950-light: #042F2E;

  /* Dark mode shades (inverted) */
  --color-primary-50-dark: #042F2E;
  --color-primary-950-dark: #F0FDFA;

  /* Active colors (default: light) */
  --color-background: var(--color-primary-50-light);
  --color-foreground: var(--color-primary-950-light);
}

.dark {
  --color-background: var(--color-primary-950-dark);
  --color-foreground: var(--color-primary-50-dark);
}
```

**Advantage**: More explicit, easier to visualize inversion.

**Recommendation**: Use Method 1 (simpler, standard pattern).

---

## Preserving Brand Identity

### Problem: Dark Mode Looks Washed Out

**Symptom**: Brand color (primary) loses vibrancy in dark mode.

**Causes**:
- Using same shade as light mode (too dark against dark background)
- Over-brightening (shade 300-400 looks neon)

**Fix**: Use shade 500 for dark mode primary (slightly brighter than shade 600 used in light).

```css
/* Light mode */
--color-primary: var(--color-primary-600); /* #0D9488 - darker for contrast on white */

/* Dark mode */
.dark {
  --color-primary: var(--color-primary-500); /* #14B8A6 - brighter for visibility */
}
```

**Result**: Brand color looks consistent between modes.

---

### Problem: Dark Mode Too Dark

**Symptom**: UI feels like a black hole, elements hard to distinguish.

**Fix**: Use shade 900 for backgrounds instead of 950.

```css
.dark {
  /* Too dark - low contrast between elements */
  --color-background: var(--color-primary-950); /* #042F2E */

  /* Better - more visible structure */
  --color-background: var(--color-primary-900); /* #134E4A */
}
```

**Trade-off**: Less contrast with pure black, but better visual hierarchy.

---

### Problem: Text Hard to Read

**Symptom**: Foreground text on dark background strains eyes.

**Causes**:
- Pure white text (`#FFFFFF`) - too harsh
- Wrong shade (900 instead of 50)

**Fix**: Use shade 50 (off-white) for dark mode text.

```css
.dark {
  /* Too harsh - pure white */
  --color-foreground: #FFFFFF;

  /* Better - off-white, easier on eyes */
  --color-foreground: var(--color-primary-50); /* #F0FDFA */
}
```

**Tip**: Reduce text opacity further for secondary text:
```tsx
<p className="text-foreground/80">Secondary text</p>
```

---

## Elevation in Dark Mode

Lighter colors = higher elevation (opposite of light mode).

### Light Mode Elevation
```
Shadows = darkness
Lower layers darker than higher layers
```

### Dark Mode Elevation
```
No shadows (or subtle)
Higher layers LIGHTER than lower layers
```

### Implementation

```css
.dark {
  /* Base layer (lowest) */
  --color-background: var(--color-primary-950); /* Darkest */

  /* Card layer (elevated) */
  --color-card: var(--color-primary-900); /* Slightly lighter */

  /* Popover layer (highest) */
  --color-popover: var(--color-primary-850); /* Even lighter */
}
```

**Note**: You may need to generate intermediate shades (850, 875) for fine-grained elevation.

---

## Borders and Dividers

Borders need higher contrast in dark mode.

### Light Mode
```css
--color-border: var(--color-primary-200); /* 87% lightness - subtle */
```

### Dark Mode
```css
.dark {
  --color-border: var(--color-primary-800); /* 27% lightness - visible */
}
```

**Guideline**: Dark mode borders should be ~10-15% lighter than background.

**Example**:
- Background: 950 (10% L)
- Border: 800 (27% L)
- Difference: 17% ✓

---

## Muted/Secondary Content

### Light Mode
```css
--color-muted: var(--color-primary-50);       /* Very light background */
--color-muted-foreground: var(--color-primary-600); /* Darker text */
```

### Dark Mode
```css
.dark {
  --color-muted: var(--color-primary-800);    /* Darker background (elevated) */
  --color-muted-foreground: var(--color-primary-400); /* Brighter text */
}
```

**Pattern**: Muted background is darker than page background (inverted), text is brighter for readability.

---

## Testing Dark Mode

### Visual Checklist
- [ ] Brand color recognizable
- [ ] Text readable without eye strain
- [ ] Borders visible but not harsh
- [ ] Buttons stand out clearly
- [ ] Focus rings obvious
- [ ] Cards/sections have clear boundaries
- [ ] No pure black or pure white (use shades)

### Automated Tests
```javascript
// Check contrast ratios
const backgroundL = 10; // shade 950
const foregroundL = 97; // shade 50
const contrast = (97 + 0.05) / (10 + 0.05); // Should be > 4.5:1

// Check for pure colors
if (background === '#000000') console.warn('Pure black used');
if (foreground === '#FFFFFF') console.warn('Pure white used');
```

---

## Common Dark Mode Mistakes

### 1. Direct Inversion (Wrong)
```css
/* ❌ This breaks contrast */
.dark {
  --color-background: var(--color-primary-50); /* Was light, now TOO light */
  --color-foreground: var(--color-primary-950); /* Was dark, now invisible */
}
```

**Fix**: Invert semantic mapping, not variable names.

### 2. Same Primary Shade
```css
/* ❌ Primary-600 too dark on dark background */
.dark {
  --color-primary: var(--color-primary-600);
}
```

**Fix**: Use brighter shade (500) in dark mode.

### 3. Forgetting Pairs
```css
/* ❌ Changed background but not foreground */
.dark {
  --color-card: var(--color-primary-900);
  /* Missing: --color-card-foreground override */
}
```

**Fix**: Always update foreground when changing background.

### 4. Pure Black Backgrounds
```css
/* ❌ Pure black shows OLED smearing, no elevation */
.dark {
  --color-background: #000000;
}
```

**Fix**: Use shade 950 or 900 (off-black).

---

## Advanced: OLED Dark Mode

For AMOLED/OLED screens, pure black saves battery.

```css
@media (prefers-contrast: high) {
  .dark {
    --color-background: #000000; /* Pure black on OLED */
    --color-card: var(--color-primary-950); /* Slight elevation */
  }
}
```

**Trade-off**: Better battery life, but less elevation hierarchy.

---

## Example: Complete Light/Dark Palette

```css
@theme {
  /* Shade scale (same in both modes) */
  --color-primary-50: #F0FDFA;
  --color-primary-500: #14B8A6;
  --color-primary-600: #0D9488;
  --color-primary-800: #115E59;
  --color-primary-900: #134E4A;
  --color-primary-950: #042F2E;

  /* Light mode */
  --color-background: #FFFFFF;
  --color-foreground: var(--color-primary-950);
  --color-card: #FFFFFF;
  --color-card-foreground: var(--color-primary-900);
  --color-primary: var(--color-primary-600);
  --color-border: var(--color-primary-200);
  --color-muted: var(--color-primary-50);
  --color-muted-foreground: var(--color-primary-600);
}

.dark {
  /* Dark mode overrides */
  --color-background: var(--color-primary-950);
  --color-foreground: var(--color-primary-50);
  --color-card: var(--color-primary-900);
  --color-card-foreground: var(--color-primary-50);
  --color-primary: var(--color-primary-500); /* Brighter */
  --color-border: var(--color-primary-800);
  --color-muted: var(--color-primary-800);
  --color-muted-foreground: var(--color-primary-400); /* Brighter */
}
```

**Result**: Consistent brand identity, readable in both modes, proper contrast.
