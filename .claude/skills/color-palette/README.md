# Color Palette

Generate complete, accessible color palettes from a single brand hex color. Creates 11-shade scales, semantic tokens, and dark mode variants with WCAG contrast checking.

## Auto-Trigger Keywords

This skill should be suggested when the user mentions:

**Technology Names:**
- color palette, colour palette, color scale, shade generation
- tailwind colors, tailwind theme, design tokens, semantic tokens
- css variables, custom properties, @theme
- hsl colors, hex to hsl, color conversion

**Use Cases:**
- brand colors, brand palette, company colors
- design system setup, theme creation
- color shades, 50-950 scale, shade scale
- light mode colors, dark mode colors, theme switching
- color inversion, dark theme, light theme

**Features:**
- semantic tokens, background foreground tokens
- color accessibility, wcag contrast, contrast ratio
- accessible colors, color contrast checking
- primary color, accent color, muted color
- card colors, border colors, ring colors

**Patterns:**
- generate shades from hex
- create color scale
- map semantic tokens
- check color contrast
- convert hex to hsl
- tailwind v4 colors
- css @theme directive

## What This Skill Covers

1. **Shade Generation** - Convert single hex to 11-shade scale (50-950)
2. **HSL Conversion** - Hex to HSL formula and lightness values
3. **Semantic Mapping** - Map shades to design tokens (background, foreground, card, etc.)
4. **Dark Mode** - Inversion patterns and shade swapping
5. **Contrast Checking** - WCAG formulas and accessibility verification
6. **Tailwind Integration** - Output using @theme syntax

## Quick Example

```css
/* Input: Brand hex #0D9488 */
@theme {
  --color-primary-50: #F0FDFA;
  --color-primary-500: #14B8A6;
  --color-primary-950: #042F2E;

  --color-background: #FFFFFF;
  --color-foreground: var(--color-primary-950);
  --color-primary: var(--color-primary-600);
}

.dark {
  --color-background: var(--color-primary-950);
  --color-foreground: var(--color-primary-50);
}
```

## Related Skills

- tailwind-v4-shadcn - Complete Tailwind v4 + shadcn/ui setup
- project-planning - Design system planning
