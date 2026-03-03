# Dark Mode Patterns

Dark mode implementation patterns using semantic color tokens.

---

## Color Token System

All patterns in this skill use semantic tokens that automatically adapt to dark mode:

| Token | Purpose | Light Example | Dark Example |
|-------|---------|---------------|--------------|
| `bg-background` | Page background | White | Dark gray |
| `bg-card` | Card backgrounds | White | Lighter gray |
| `bg-muted` | Subtle backgrounds | Light gray | Medium gray |
| `bg-accent` | Highlighted areas | Very light | Medium |
| `text-foreground` | Primary text | Dark gray | White |
| `text-muted-foreground` | Secondary text | Gray | Light gray |
| `border-border` | All borders | Light gray | Dark gray |
| `bg-primary` | Brand color | Blue 500 | Blue 400 |
| `bg-secondary` | Secondary actions | Gray | Light gray |
| `bg-destructive` | Errors/deletes | Red | Lighter red |

---

## Critical Rules

### ✅ Always Use Semantic Tokens

```tsx
// ✅ CORRECT - Adapts to dark mode automatically
<div className="bg-card text-card-foreground border-border">
  <p className="text-muted-foreground">Content</p>
</div>
```

### ❌ Never Use Raw Colors

```tsx
// ❌ WRONG - Breaks in dark mode
<div className="bg-white text-gray-900 border-gray-200">
  <p className="text-gray-600">Content</p>
</div>

// ❌ WRONG - Manual dark: variants defeat the purpose
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Content
</div>
```

---

## Theme Toggle Implementation

### Basic Theme Provider

Create `components/theme-provider.tsx`:

```tsx
'use client'

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeProviderContext = createContext<ThemeProviderState | undefined>(undefined)

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'theme',
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(defaultTheme)

  useEffect(() => {
    // Load theme from storage
    const stored = localStorage.getItem(storageKey) as Theme | null
    if (stored) {
      setTheme(stored)
    }
  }, [storageKey])

  useEffect(() => {
    const root = window.document.documentElement

    // Remove previous theme classes
    root.classList.remove('light', 'dark')

    // Apply new theme
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      root.classList.add(systemTheme)
    } else {
      root.classList.add(theme)
    }

    // Save to storage
    localStorage.setItem(storageKey, theme)
  }, [theme, storageKey])

  return (
    <ThemeProviderContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeProviderContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

### Wrap Your App

In `main.tsx` or `app.tsx`:

```tsx
import { ThemeProvider } from '@/components/theme-provider'

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="app-theme">
      {/* Your app */}
    </ThemeProvider>
  )
}
```

### Theme Toggle Component

Create `components/mode-toggle.tsx`:

```tsx
'use client'

import { useTheme } from '@/components/theme-provider'

export function ModeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <button
      onClick={() => {
        if (theme === 'light') setTheme('dark')
        else if (theme === 'dark') setTheme('system')
        else setTheme('light')
      }}
      className="p-2 rounded-md hover:bg-accent transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'light' && (
        <svg className="h-5 w-5">☀️</svg>
      )}
      {theme === 'dark' && (
        <svg className="h-5 w-5">🌙</svg>
      )}
      {theme === 'system' && (
        <svg className="h-5 w-5">💻</svg>
      )}
    </button>
  )
}
```

---

## Testing Dark Mode

### Visual Check

After implementing semantic tokens:

1. Toggle between light/dark modes
2. Check all components for readability
3. Verify borders are visible
4. Ensure hover states work
5. Test form inputs for contrast

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Text unreadable | Using raw `text-gray-600` | Use `text-muted-foreground` |
| Borders invisible | Using `border-gray-200` | Use `border-border` |
| Cards blend in | Using `bg-white` | Use `bg-card` |
| Buttons wrong color | Using `bg-blue-500` | Use `bg-primary` |

---

## Component Patterns

### Card (Dark Mode Ready)

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  <h3 className="text-lg font-semibold mb-2">Card Title</h3>
  <p className="text-muted-foreground">Card content</p>
</div>
```

### Form Input (Dark Mode Ready)

```tsx
<input
  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:ring-2 focus:ring-primary"
  placeholder="Dark mode compatible"
/>
```

### Button (Dark Mode Ready)

```tsx
<button className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
  Click Me
</button>
```

---

## Advanced: Custom Colors

If you need custom colors beyond semantic tokens, define them in CSS:

```css
:root {
  --brand-blue: #3b82f6;
}

.dark {
  --brand-blue: #60a5fa;
}
```

Then use in Tailwind:

```tsx
<div style={{ backgroundColor: 'var(--brand-blue)' }}>
  Custom color that adapts
</div>
```

---

## Best Practices

### ✅ Do

- Use semantic color tokens exclusively
- Test in both light and dark modes
- Provide theme toggle in header
- Respect system preference by default
- Save theme preference to localStorage
- Use `transition-colors` for smooth theme switches

### ❌ Don't

- Use raw Tailwind colors (`bg-blue-500`)
- Manually add `dark:` variants everywhere
- Forget to test hover states in dark mode
- Force one theme without toggle
- Use hard-coded color values
- Skip border colors (often invisible in dark mode)

---

## Migration from Raw Colors

If you have existing components with raw colors:

```tsx
// Before (breaks in dark mode)
<div className="bg-white text-gray-900 border-gray-200">
  <p className="text-gray-600">Content</p>
</div>

// After (dark mode compatible)
<div className="bg-card text-card-foreground border-border">
  <p className="text-muted-foreground">Content</p>
</div>
```

**Conversion mapping**:
- `bg-white` → `bg-background` or `bg-card`
- `text-gray-900` → `text-foreground`
- `text-gray-600` → `text-muted-foreground`
- `border-gray-200` → `border-border`
- `bg-gray-100` → `bg-muted`
- `bg-blue-500` → `bg-primary`

---

**Related**: See all reference files for semantic token usage examples.
