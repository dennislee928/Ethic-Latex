# Icon Library Comparison

Detailed comparison of Lucide, Heroicons, and Phosphor icon libraries.

## Overview

| Feature | Lucide | Heroicons | Phosphor |
|---------|--------|-----------|----------|
| **Icons** | 1,400+ | 292 | 7,000+ |
| **Weights** | 1 | 2 (outline, solid) | 6 (thin→fill) |
| **Package** | `lucide-react` | `@heroicons/react` | `@phosphor-icons/react` |
| **Size (gzip)** | ~5KB per icon set | ~3KB | ~7KB |
| **Tree-shakeable** | Yes | Yes | Yes |
| **License** | ISC | MIT | MIT |
| **Origin** | Fork of Feather | Tailwind Labs | Independent |

## When to Use Each

### Lucide (Default Recommendation)

**Best for:**
- React/Vue/Svelte projects
- General-purpose applications
- When you need variety (1,400+ icons)
- Teams already familiar with Feather Icons

**Installation:**
```bash
npm install lucide-react
```

**Usage:**
```tsx
import { Home, Settings, User } from 'lucide-react'

<Home className="w-6 h-6" />
<Settings className="w-6 h-6" strokeWidth={1.5} />
```

**Pros:**
- Large library with frequent updates
- Excellent React integration
- Fork of popular Feather Icons
- PascalCase component names
- Customizable stroke width

**Cons:**
- No weight variations (outline only)
- Some inconsistency from community contributions

---

### Heroicons

**Best for:**
- Tailwind CSS projects
- Minimal, clean aesthetic
- Projects using Tailwind UI components
- When you need outline AND solid variants

**Installation:**
```bash
npm install @heroicons/react
```

**Usage:**
```tsx
// Outline (24px)
import { HomeIcon } from '@heroicons/react/24/outline'

// Solid (24px)
import { HomeIcon } from '@heroicons/react/24/solid'

// Mini (20px)
import { HomeIcon } from '@heroicons/react/20/solid'

<HomeIcon className="w-6 h-6" />
```

**Pros:**
- Official Tailwind integration
- Consistent, polished design
- Two styles (outline/solid) per icon
- Three sizes (16, 20, 24px)
- kebab-case naming matches Tailwind

**Cons:**
- Smaller library (292 icons)
- Only 2 weight variations
- Import paths can be verbose

---

### Phosphor

**Best for:**
- When you need weight variations (thin, light, regular, bold, fill, duotone)
- Large icon needs (7,000+ icons)
- Design-heavy projects
- When brand consistency requires specific weights

**Installation:**
```bash
npm install @phosphor-icons/react
```

**Usage:**
```tsx
import { House, Gear, User } from '@phosphor-icons/react'

// Default (regular weight)
<House size={24} />

// Specific weights
<House size={24} weight="thin" />
<House size={24} weight="light" />
<House size={24} weight="regular" />
<House size={24} weight="bold" />
<House size={24} weight="fill" />
<House size={24} weight="duotone" />
```

**Pros:**
- Largest library (7,000+ icons)
- 6 weight variations per icon
- Consistent design language
- Duotone variant is unique

**Cons:**
- Larger bundle if using multiple weights
- Less React-ecosystem adoption
- PascalCase differs from Tailwind conventions

---

## Import Patterns

### Tree-Shaking Safe

All three libraries support tree-shaking when importing specific icons:

```tsx
// Lucide - GOOD
import { Home, User, Settings } from 'lucide-react'

// Heroicons - GOOD
import { HomeIcon, UserIcon } from '@heroicons/react/24/outline'

// Phosphor - GOOD
import { House, User, Gear } from '@phosphor-icons/react'
```

### Dynamic Icons (All Libraries)

**Never do this** (breaks tree-shaking):
```tsx
import * as Icons from 'lucide-react'
const Icon = Icons[iconName]  // All icons bundled!
```

**Do this instead** (explicit map):
```tsx
import { Home, User, Settings, type LucideIcon } from 'lucide-react'

const ICON_MAP: Record<string, LucideIcon> = {
  home: Home,
  user: User,
  settings: Settings,
}

const Icon = ICON_MAP[iconName]
```

---

## Size Comparison

For a typical project using 20 icons:

| Library | Bundle Impact |
|---------|---------------|
| Lucide | ~15KB |
| Heroicons | ~12KB |
| Phosphor (single weight) | ~18KB |
| Phosphor (6 weights) | ~100KB |

---

## Recommendation Matrix

| Project Type | Recommended Library |
|--------------|---------------------|
| React + Tailwind | Heroicons or Lucide |
| React general | Lucide |
| Vue/Svelte | Lucide |
| Design-heavy, brand-consistent | Phosphor |
| Minimal bundle size | Heroicons |
| Maximum icon variety | Phosphor |
| Legacy Feather migration | Lucide |
