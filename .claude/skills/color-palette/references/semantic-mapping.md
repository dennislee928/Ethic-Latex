# Semantic Token Mapping Reference

Map shade scale to semantic tokens for components and UI patterns.

---

## Core Semantic Tokens

### Light Mode

| Token | Shade | Hex (Teal example) | Use Case |
|-------|-------|--------------------|----------|
| `background` | white | `#FFFFFF` | Page/card backgrounds |
| `foreground` | 950 | `#042F2E` | Body text |
| `card` | white | `#FFFFFF` | Card backgrounds |
| `card-foreground` | 900 | `#134E4A` | Card text |
| `popover` | white | `#FFFFFF` | Dropdown/tooltip backgrounds |
| `popover-foreground` | 950 | `#042F2E` | Dropdown text |
| `primary` | 600 | `#0D9488` | Primary buttons, links |
| `primary-foreground` | white | `#FFFFFF` | Text on primary buttons |
| `secondary` | 100 | `#CCFBF1` | Secondary buttons |
| `secondary-foreground` | 900 | `#134E4A` | Text on secondary buttons |
| `muted` | 50 | `#F0FDFA` | Disabled backgrounds, subtle sections |
| `muted-foreground` | 600 | `#0D9488` | Muted text, captions |
| `accent` | 100 | `#CCFBF1` | Hover states, subtle highlights |
| `accent-foreground` | 900 | `#134E4A` | Text on accent backgrounds |
| `destructive` | red-600 | `#DC2626` | Delete buttons, errors |
| `destructive-foreground` | white | `#FFFFFF` | Text on destructive buttons |
| `border` | 200 | `#99F6E4` | Input borders, dividers |
| `input` | 200 | `#99F6E4` | Input field borders |
| `ring` | 600 | `#0D9488` | Focus rings |

### Dark Mode

| Token | Shade | Hex (Teal example) | Use Case |
|-------|-------|--------------------|----------|
| `background` | 950 | `#042F2E` | Page/card backgrounds |
| `foreground` | 50 | `#F0FDFA` | Body text |
| `card` | 900 | `#134E4A` | Card backgrounds |
| `card-foreground` | 50 | `#F0FDFA` | Card text |
| `popover` | 900 | `#134E4A` | Dropdown backgrounds |
| `popover-foreground` | 50 | `#F0FDFA` | Dropdown text |
| `primary` | 500 | `#14B8A6` | Primary buttons (brighter in dark) |
| `primary-foreground` | white | `#FFFFFF` | Text on primary buttons |
| `secondary` | 800 | `#115E59` | Secondary buttons |
| `secondary-foreground` | 50 | `#F0FDFA` | Text on secondary buttons |
| `muted` | 800 | `#115E59` | Disabled backgrounds |
| `muted-foreground` | 400 | `#2DD4BF` | Muted text |
| `accent` | 800 | `#115E59` | Hover states |
| `accent-foreground` | 50 | `#F0FDFA` | Text on accent backgrounds |
| `destructive` | red-500 | `#EF4444` | Delete buttons (brighter) |
| `destructive-foreground` | white | `#FFFFFF` | Text on destructive |
| `border` | 800 | `#115E59` | Borders |
| `input` | 800 | `#115E59` | Input borders |
| `ring` | 500 | `#14B8A6` | Focus rings |

---

## CSS Output Template (Tailwind v4 @theme)

```css
@import "tailwindcss";

@theme {
  /* Shade scale */
  --color-primary-50: #F0FDFA;
  --color-primary-100: #CCFBF1;
  --color-primary-200: #99F6E4;
  --color-primary-300: #5EEAD4;
  --color-primary-400: #2DD4BF;
  --color-primary-500: #14B8A6;
  --color-primary-600: #0D9488;
  --color-primary-700: #0F766E;
  --color-primary-800: #115E59;
  --color-primary-900: #134E4A;
  --color-primary-950: #042F2E;

  /* Light mode semantic tokens */
  --color-background: #FFFFFF;
  --color-foreground: var(--color-primary-950);

  --color-card: #FFFFFF;
  --color-card-foreground: var(--color-primary-900);

  --color-popover: #FFFFFF;
  --color-popover-foreground: var(--color-primary-950);

  --color-primary: var(--color-primary-600);
  --color-primary-foreground: #FFFFFF;

  --color-secondary: var(--color-primary-100);
  --color-secondary-foreground: var(--color-primary-900);

  --color-muted: var(--color-primary-50);
  --color-muted-foreground: var(--color-primary-600);

  --color-accent: var(--color-primary-100);
  --color-accent-foreground: var(--color-primary-900);

  --color-destructive: #DC2626;
  --color-destructive-foreground: #FFFFFF;

  --color-border: var(--color-primary-200);
  --color-input: var(--color-primary-200);
  --color-ring: var(--color-primary-600);

  --radius: 0.5rem;
}

/* Dark mode overrides */
.dark {
  --color-background: var(--color-primary-950);
  --color-foreground: var(--color-primary-50);

  --color-card: var(--color-primary-900);
  --color-card-foreground: var(--color-primary-50);

  --color-popover: var(--color-primary-900);
  --color-popover-foreground: var(--color-primary-50);

  --color-primary: var(--color-primary-500);
  --color-primary-foreground: #FFFFFF;

  --color-secondary: var(--color-primary-800);
  --color-secondary-foreground: var(--color-primary-50);

  --color-muted: var(--color-primary-800);
  --color-muted-foreground: var(--color-primary-400);

  --color-accent: var(--color-primary-800);
  --color-accent-foreground: var(--color-primary-50);

  --color-destructive: #EF4444;
  --color-destructive-foreground: #FFFFFF;

  --color-border: var(--color-primary-800);
  --color-input: var(--color-primary-800);
  --color-ring: var(--color-primary-500);
}
```

---

## Usage in Components

### Buttons

```tsx
// Primary button
<button className="bg-primary text-primary-foreground hover:bg-primary/90">
  Click me
</button>

// Secondary button
<button className="bg-secondary text-secondary-foreground hover:bg-secondary/80">
  Cancel
</button>

// Destructive button
<button className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
  Delete
</button>
```

### Cards

```tsx
<div className="bg-card text-card-foreground border-border rounded-lg">
  <h2>Card Title</h2>
  <p className="text-muted-foreground">Card description</p>
</div>
```

### Inputs

```tsx
<input
  className="bg-background text-foreground border-input focus:ring-ring"
  placeholder="Enter text"
/>
```

### Muted Text

```tsx
<p className="text-muted-foreground">
  This is secondary/helper text
</p>
```

---

## Token Pairing Rules

**CRITICAL**: Every background token MUST have a paired foreground token.

| Background | Foreground | Why |
|------------|------------|-----|
| `background` | `foreground` | Main page text |
| `card` | `card-foreground` | Card text readability |
| `popover` | `popover-foreground` | Dropdown text |
| `primary` | `primary-foreground` | Button text contrast |
| `secondary` | `secondary-foreground` | Secondary button contrast |
| `muted` | `muted-foreground` | Muted section text |
| `accent` | `accent-foreground` | Accent section text |
| `destructive` | `destructive-foreground` | Error button text |

**Never** use a background token without its foreground pair, or dark mode will break.

---

## Primary Color Usage

The `primary` color is your brand identity. Use it for:

### Primary Actions
- Call-to-action buttons
- Primary navigation links
- Active states
- Selected items
- Progress indicators

### Focus States
- Focus rings on inputs
- Keyboard navigation highlights
- Active form fields

### Brand Elements
- Logos (when appropriate)
- Brand-colored sections
- Accent text for emphasis
- Icons for primary actions

**Avoid overuse**: Too much primary color dilutes brand impact. Use sparingly for important UI elements.

---

## Adjusting for Brand Identity

### Conservative Brands (Finance, Law, Healthcare)
- Use darker primary shade (700) for buttons
- Reduce saturation in light shades (50-300)
- Prefer muted over accent
- More neutral grays

```css
--color-primary: var(--color-primary-700); /* Darker, more serious */
```

### Vibrant Brands (Creative, Tech, Entertainment)
- Use brighter primary shade (500-600)
- Keep full saturation
- Use accent more liberally
- Bold contrast ratios

```css
--color-primary: var(--color-primary-500); /* Bright and energetic */
```

### Minimal Brands (Design, Architecture)
- Use primary sparingly
- Emphasize muted and neutral tones
- Subtle borders (primary-100 instead of 200)
- Larger white space

```css
--color-border: var(--color-primary-100); /* Barely visible borders */
```

---

## Multi-Color Palettes

For designs with multiple brand colors:

```css
@theme {
  /* Primary (brand color) */
  --color-primary-*: /* teal shades */

  /* Accent (complementary) */
  --color-accent-50: #FFF7ED;
  --color-accent-600: #EA580C; /* Orange */
  --color-accent-950: #431407;

  /* Use accent for secondary CTAs, highlights */
}
```

**Pattern**: Generate separate shade scales for each brand color, map to different semantic roles.

---

## Verification Checklist

- [ ] Every background has a foreground pair
- [ ] Contrast meets WCAG AA (check with `references/contrast-checking.md`)
- [ ] Light and dark modes are consistent (same token names)
- [ ] Primary color is recognizable in both modes
- [ ] Muted text is readable but not prominent
- [ ] Borders are visible but not distracting
- [ ] Focus rings stand out clearly

**Test in both modes** before finalizing.
