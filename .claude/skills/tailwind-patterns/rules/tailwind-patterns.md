# Tailwind Patterns Correction Rules

Corrections for common Tailwind CSS pattern mistakes.

---

## Semantic Colors (Critical)

### ❌ Wrong: Raw Tailwind Colors

```tsx
// DON'T - Breaks dark mode
<div className="bg-white text-gray-900 border-gray-200">
  <p className="text-gray-600">Content</p>
  <button className="bg-blue-500 text-white">Click</button>
</div>
```

### ✅ Correct: Semantic Color Tokens

```tsx
// DO - Works in both light and dark mode
<div className="bg-card text-card-foreground border-border">
  <p className="text-muted-foreground">Content</p>
  <button className="bg-primary text-primary-foreground">Click</button>
</div>
```

**Why**: Raw colors like `bg-blue-500` don't adapt to dark mode. Semantic tokens (`bg-primary`, `text-foreground`) automatically adjust.

---

## Responsive Design

### ❌ Wrong: Non-Responsive Patterns

```tsx
// DON'T - Fixed sizes, no breakpoints
<h1 className="text-6xl">Title</h1>
<div className="grid grid-cols-3 gap-6">
  {items.map(item => <Card key={item.id} />)}
</div>
```

### ✅ Correct: Mobile-First Responsive

```tsx
// DO - Scales from mobile to desktop
<h1 className="text-4xl sm:text-5xl lg:text-6xl">Title</h1>
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => <Card key={item.id} />)}
</div>
```

**Why**: Mobile devices are the majority of traffic. Start small and grow with breakpoints.

---

## Spacing Consistency

### ❌ Wrong: Random Spacing Values

```tsx
// DON'T - Inconsistent spacing
<div className="p-5 mb-7 gap-3">
  <div className="mt-9 mb-11">Content</div>
</div>
```

### ✅ Correct: Consistent Spacing Scale

```tsx
// DO - Use scale of 4, 6, 8, 12, 16, 24
<div className="p-6 mb-8 gap-4">
  <div className="mt-8 mb-12">Content</div>
</div>
```

**Why**: Consistent spacing creates visual rhythm and prevents design drift.

**Standard scale**:
- Tight: 2, 4
- Standard: 6, 8
- Loose: 12, 16
- Section: 16, 24

---

## Hover and Focus States

### ❌ Wrong: No Interactive States

```tsx
// DON'T - No hover feedback
<button className="bg-primary text-primary-foreground px-4 py-2 rounded-md">
  Click
</button>

<a href="#" className="text-primary">
  Link
</a>
```

### ✅ Correct: Clear Interactive States

```tsx
// DO - Hover and focus states
<button className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors focus:ring-2 focus:ring-primary">
  Click
</button>

<a href="#" className="text-primary hover:underline underline-offset-4 focus:outline-none focus:ring-2 focus:ring-primary">
  Link
</a>
```

**Why**: Users need visual feedback that elements are interactive.

---

## Grid Truncation

### ❌ Wrong: Missing `min-w-0` on Grid Items

```tsx
// DON'T - Text overflows into adjacent cells
<div className="grid grid-cols-3">
  <div>Very long text that overflows...</div>
</div>
```

### ✅ Correct: `min-w-0` + `truncate`

```tsx
// DO - Truncate with ellipsis
<div className="grid grid-cols-3">
  <div className="min-w-0">
    <span className="truncate" title="Full text here">
      Very long text that overflows...
    </span>
  </div>
</div>
```

**Why**: Grid items have implicit `min-width: auto` which prevents shrinking below content width.

---

## Dark Mode: Manual Variants

### ❌ Wrong: Manual `dark:` Variants

```tsx
// DON'T - Defeats purpose of semantic tokens
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  <p className="text-gray-600 dark:text-gray-300">Content</p>
</div>
```

### ✅ Correct: Semantic Tokens Handle Dark Mode

```tsx
// DO - Automatically adapts
<div className="bg-card text-card-foreground">
  <p className="text-muted-foreground">Content</p>
</div>
```

**Why**: Semantic tokens already include dark mode variants. Manual `dark:` classes are redundant and error-prone.

---

## Container Patterns

### ❌ Wrong: Inconsistent Container Usage

```tsx
// DON'T - Missing responsive padding
<div className="max-w-7xl mx-auto">
  <h1>Title</h1>
</div>
```

### ✅ Correct: Consistent Container Pattern

```tsx
// DO - Standard container with padding
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <h1>Title</h1>
</div>
```

**Why**: Content needs horizontal padding on mobile to prevent edge-touching.

---

## Text Sizing

### ❌ Wrong: Fixed px Values

```tsx
// DON'T - Not responsive, not accessible
<p className="text-[16px]">Content</p>
<h1 className="text-[48px]">Title</h1>
```

### ✅ Correct: Tailwind Size Classes

```tsx
// DO - Responsive and scalable
<p className="text-base">Content</p>
<h1 className="text-4xl sm:text-5xl lg:text-6xl">Title</h1>
```

**Why**: Tailwind's size classes respect user font size preferences and scale better.

---

## Button Sizing

### ❌ Wrong: No Consistent Touch Targets

```tsx
// DON'T - Too small for mobile
<button className="px-2 py-1 text-xs">
  Click
</button>
```

### ✅ Correct: Minimum 44x44px Touch Target

```tsx
// DO - Mobile-friendly sizing
<button className="px-4 py-2 text-sm">
  Click
</button>

// Icon-only buttons need explicit sizing
<button className="h-10 w-10 flex items-center justify-center">
  <svg className="h-5 w-5">Icon</svg>
</button>
```

**Why**: iOS and Android guidelines recommend 44x44px minimum touch targets.

---

## Z-Index Organization

### ❌ Wrong: Random Z-Index Values

```tsx
// DON'T - Unmaintainable stacking
<div className="z-[999]">Modal</div>
<div className="z-[100]">Header</div>
<div className="z-[9999]">Tooltip</div>
```

### ✅ Correct: Systematic Z-Index Scale

```tsx
// DO - Organized layers (increments of 10)
<div className="z-0">Background</div>
<div className="z-10">Content</div>
<div className="z-20">Dropdowns</div>
<div className="z-40">Fixed header</div>
<div className="z-50">Modals</div>
<div className="z-[60]">Tooltips</div>
```

**Why**: Systematic z-index makes layering predictable and maintainable.

---

## Form Validation States

### ❌ Wrong: No Visual Feedback

```tsx
// DON'T - No indication of error
<input
  type="email"
  className="w-full px-3 py-2 bg-background border border-border rounded-md"
/>
<p className="text-sm">Invalid email</p>
```

### ✅ Correct: Clear Error Styling

```tsx
// DO - Visual error indicators
<input
  type="email"
  className="w-full px-3 py-2 bg-background border border-destructive rounded-md focus:ring-2 focus:ring-destructive"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<p id="email-error" className="text-sm text-destructive">
  Invalid email address
</p>
```

**Why**: Users need clear visual indication of validation errors.

---

## Image Aspect Ratios

### ❌ Wrong: No Aspect Ratio Constraints

```tsx
// DON'T - Images cause layout shift
<img src="/image.jpg" alt="" className="w-full" />
```

### ✅ Correct: Fixed Aspect Ratios

```tsx
// DO - Maintain consistent aspect ratio
<div className="aspect-video">
  <img src="/image.jpg" alt="" className="w-full h-full object-cover" />
</div>

// Or for square images
<div className="aspect-square">
  <img src="/image.jpg" alt="" className="w-full h-full object-cover" />
</div>
```

**Why**: Prevents cumulative layout shift (CLS) and maintains visual consistency.

---

## Transition Performance

### ❌ Wrong: Animating Layout Properties

```tsx
// DON'T - Causes reflow (janky)
<div className="transition-all hover:w-64 hover:h-64 hover:top-10 hover:left-10">
  Content
</div>
```

### ✅ Correct: Animate Transform/Opacity Only

```tsx
// DO - GPU-accelerated (smooth)
<div className="transition-transform hover:scale-105">
  Content
</div>

<div className="transition-opacity hover:opacity-80">
  Content
</div>
```

**Why**: Transform and opacity are GPU-accelerated. Width, height, top, left cause reflow.

---

## Apply These Corrections

When you see patterns that violate these rules, automatically apply the corrections shown above.

**Priority order**:
1. Semantic colors (breaks dark mode)
2. Responsive design (breaks mobile)
3. Spacing consistency (visual quality)
4. Interactive states (usability)
5. Performance (smooth UX)
