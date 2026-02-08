# Button Patterns

Complete button styling guide for Tailwind CSS projects.

---

## Button Variants

### Primary Button

```tsx
<button className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors">
  Primary
</button>
```

### Secondary Button

```tsx
<button className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/80 transition-colors">
  Secondary
</button>
```

### Outline Button

```tsx
<button className="border border-border bg-transparent px-4 py-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors">
  Outline
</button>
```

### Ghost Button

```tsx
<button className="bg-transparent px-4 py-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors">
  Ghost
</button>
```

### Destructive Button

```tsx
<button className="bg-destructive text-destructive-foreground px-4 py-2 rounded-md hover:bg-destructive/90 transition-colors">
  Delete
</button>
```

### Link Button

```tsx
<button className="text-primary underline-offset-4 hover:underline">
  Link
</button>
```

---

## Button Sizes

### Small

```tsx
<button className="bg-primary text-primary-foreground px-3 py-1.5 text-sm rounded-md hover:bg-primary/90">
  Small
</button>
```

### Default

```tsx
<button className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
  Default
</button>
```

### Large

```tsx
<button className="bg-primary text-primary-foreground px-6 py-3 text-lg rounded-md hover:bg-primary/90">
  Large
</button>
```

---

## Button States

### Disabled

```tsx
<button
  disabled
  className="bg-primary text-primary-foreground px-4 py-2 rounded-md opacity-50 cursor-not-allowed"
>
  Disabled
</button>
```

### Loading

```tsx
<button
  disabled
  className="bg-primary text-primary-foreground px-4 py-2 rounded-md opacity-75 cursor-wait flex items-center gap-2"
>
  <svg className="h-4 w-4 animate-spin">⟳</svg>
  Loading...
</button>
```

### Success

```tsx
<button className="bg-success text-success-foreground px-4 py-2 rounded-md hover:bg-success/90 flex items-center gap-2">
  <svg className="h-4 w-4">✓</svg>
  Success
</button>
```

---

## Button with Icons

### Icon Left

```tsx
<button className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 flex items-center gap-2">
  <svg className="h-4 w-4">📥</svg>
  Download
</button>
```

### Icon Right

```tsx
<button className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 flex items-center gap-2">
  Continue
  <svg className="h-4 w-4">→</svg>
</button>
```

### Icon Only

```tsx
<button
  className="bg-primary text-primary-foreground h-10 w-10 rounded-md hover:bg-primary/90 flex items-center justify-center"
  aria-label="Settings"
>
  <svg className="h-5 w-5">⚙️</svg>
</button>
```

---

## Button Groups

### Horizontal Group

```tsx
<div className="inline-flex rounded-md shadow-sm">
  <button className="px-4 py-2 bg-primary text-primary-foreground rounded-l-md hover:bg-primary/90">
    Left
  </button>
  <button className="px-4 py-2 bg-primary text-primary-foreground border-l border-primary-foreground/20 hover:bg-primary/90">
    Middle
  </button>
  <button className="px-4 py-2 bg-primary text-primary-foreground border-l border-primary-foreground/20 rounded-r-md hover:bg-primary/90">
    Right
  </button>
</div>
```

### Segmented Control

```tsx
<div className="inline-flex gap-1 p-1 bg-muted rounded-lg">
  <button className="px-4 py-2 text-sm font-medium bg-background rounded-md shadow">
    Active
  </button>
  <button className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">
    Inactive
  </button>
  <button className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">
    Inactive
  </button>
</div>
```

---

## Full Width Buttons

```tsx
<button className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
  Full Width Button
</button>
```

---

## Floating Action Button (FAB)

```tsx
<button className="fixed bottom-8 right-8 h-14 w-14 bg-primary text-primary-foreground rounded-full shadow-lg hover:bg-primary/90 hover:shadow-xl transition-all flex items-center justify-center">
  <svg className="h-6 w-6">+</svg>
</button>
```

---

## Best Practices

### ✅ Do

- Use semantic color tokens
- Add `transition-colors` for smooth hover effects
- Include `disabled:` variants for disabled states
- Use `flex items-center gap-2` for icon + text
- Set min-width for consistent sizing
- Add appropriate `aria-label` for icon-only buttons

### ❌ Don't

- Use raw colors like `bg-blue-500`
- Skip hover states
- Make buttons too small (<44px touch target)
- Use `<div>` for clickable buttons
- Forget disabled state styling
- Remove focus ring without replacement

---

**Related**: See `form-patterns.md` for submit buttons, `navigation-patterns.md` for CTA placement.
