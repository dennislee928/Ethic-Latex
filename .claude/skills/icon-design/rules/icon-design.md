# Icon Design Rules

Correction rules for icon usage in React/TypeScript projects.

## Never Use Emoji for UI Icons

Emoji render inconsistently across platforms and can't be styled.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<span>✅</span>` | `<Check className="w-4 h-4" />` |
| `<span>⚠️</span>` | `<AlertTriangle className="w-4 h-4" />` |
| `✉️ Email` | `<Mail className="w-4 h-4" /> Email` |
| `📍 Location` | `<MapPin className="w-4 h-4" /> Location` |

## Tree-Shaking Prevention

Dynamic icon access breaks tree-shaking, bundling ALL icons.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `import * as Icons from 'lucide-react'` | Named imports only |
| `Icons[iconName]` | Explicit `ICON_MAP` object |
| `require('lucide-react')[name]` | Static imports |

Correct pattern:

```tsx
import { Home, User, Settings, type LucideIcon } from 'lucide-react'

const ICON_MAP: Record<string, LucideIcon> = {
  home: Home,
  user: User,
  settings: Settings,
}

const Icon = ICON_MAP[iconName]
if (!Icon) throw new Error(`Unknown icon: ${iconName}`)
```

## Use Semantic Colours

Icons should use Tailwind v4 semantic tokens, not raw colours.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `className="text-blue-500"` | `className="text-primary"` |
| `className="text-gray-500"` | `className="text-muted-foreground"` |
| `className="text-red-500"` | `className="text-destructive"` |
| `stroke="#3B82F6"` | `className="text-primary"` (uses currentColor) |

## Consistent Sizing

Use standard size classes within a section.

| Context | Class | Notes |
|---------|-------|-------|
| Inline text | `w-4 h-4` or `w-5 h-5` | Match line height |
| Feature cards | `w-6 h-6` to `w-8 h-8` | Inside container |
| Hero sections | `w-10 h-10` to `w-12 h-12` | Decorative |

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Mixed sizes in one section | Same size for all icons in section |
| `size={24}` (Phosphor) | `className="w-6 h-6"` (Tailwind) |
| `width="20" height="20"` | `className="w-5 h-5"` |

## Style Consistency

Never mix outline and solid icons in the same section.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `CheckIcon` (solid) next to `HomeIcon` (outline) | All outline OR all solid |
| Heroicons `/24/outline` mixed with `/24/solid` | Pick one style for section |
| Phosphor `weight="fill"` mixed with `weight="regular"` | Single weight per section |

## Heroicons Import Paths

Heroicons have specific import paths for sizes and styles.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `@heroicons/react/outline` | `@heroicons/react/24/outline` |
| `@heroicons/react/solid` | `@heroicons/react/24/solid` |
| `import { Home }` | `import { HomeIcon }` (suffix required) |

Correct patterns:

```tsx
// 24px outline (default)
import { HomeIcon } from '@heroicons/react/24/outline'

// 24px solid
import { HomeIcon } from '@heroicons/react/24/solid'

// 20px solid (mini)
import { HomeIcon } from '@heroicons/react/20/solid'
```

## Accessibility

Decorative icons need proper handling.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<Icon />` (no label) | `<Icon aria-hidden="true" />` or with `aria-label` |
| Icon-only button without label | Add `aria-label="Description"` to button |

Correct patterns:

```tsx
// Decorative icon (alongside text)
<span className="flex items-center gap-2">
  <Phone aria-hidden="true" className="w-4 h-4" />
  <span>Call us</span>
</span>

// Icon-only button
<button aria-label="Open menu">
  <Menu className="w-6 h-6" />
</button>

// Meaningful standalone icon
<CheckCircle aria-label="Completed" className="w-5 h-5 text-green-500" />
```

## Lucide Wrapper Elements

Lucide icons don't accept HTML attributes like `title` directly.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `<Trophy title="Award" />` | `<span title="Award"><Trophy /></span>` |
| `<Icon aria-label="..." />` | Wrap in element with aria-label |

## currentColor Pattern

Icons should inherit colour from parent text.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `stroke="#000000"` | Use default (currentColor) |
| `fill="blue"` | `className="text-primary"` |
| Hardcoded colours in SVG | Let CSS control via currentColor |
