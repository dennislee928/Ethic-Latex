# Layout Patterns

Responsive layout patterns for Tailwind CSS projects.

---

## Container Patterns

### Standard Page Container

Maximum width with responsive horizontal padding:

```tsx
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  {/* Page content */}
</div>
```

**Breakdown**:
- `max-w-7xl` - Maximum width 1280px
- `mx-auto` - Center horizontally
- `px-4 sm:px-6 lg:px-8` - Responsive padding (16px → 24px → 32px)

### Container Width Variations

```tsx
// Narrow (blog posts, articles)
<div className="max-w-4xl mx-auto px-4">

// Medium (forms, dashboards)
<div className="max-w-5xl mx-auto px-4 sm:px-6">

// Wide (content with sidebar)
<div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

// Full width (landing pages)
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

// Extra wide (dashboards)
<div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
```

### Full-Width Section with Contained Content

```tsx
<section className="w-full bg-muted">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
    {/* Section content */}
  </div>
</section>
```

---

## Section Spacing

### Standard Section

```tsx
<section className="py-16 sm:py-24">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    {/* Section content */}
  </div>
</section>
```

**Breakdown**:
- `py-16` - 64px vertical padding (mobile)
- `sm:py-24` - 96px vertical padding (tablet+)

### Section Variations

```tsx
// Compact section
<section className="py-12 sm:py-16">

// Standard section
<section className="py-16 sm:py-24">

// Spacious section
<section className="py-24 sm:py-32">

// Hero section
<section className="py-32 sm:py-40 lg:py-48">
```

### Alternating Background Sections

```tsx
<div>
  {/* Light background */}
  <section className="py-16 sm:py-24 bg-background">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Content */}
    </div>
  </section>

  {/* Accent background */}
  <section className="py-16 sm:py-24 bg-muted">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Content */}
    </div>
  </section>

  {/* Light background */}
  <section className="py-16 sm:py-24 bg-background">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Content */}
    </div>
  </section>
</div>
```

---

## Grid Layouts

### Responsive Grid (Fixed Breakpoints)

```tsx
// 1 column mobile → 2 tablet → 3 desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// 1 column mobile → 2 tablet → 4 desktop
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// 2 columns mobile → 3 tablet → 4 desktop → 6 extra large
<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

### Auto-Fit Grid (Dynamic Columns)

Automatically adjusts number of columns based on available space:

```tsx
<div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

**When to use**:
- Unknown number of items
- Items should fill available space
- Prefer automatic column calculation

### Auto-Fill Grid

Similar to auto-fit, but creates empty columns if space available:

```tsx
<div className="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

**Difference from auto-fit**: auto-fill maintains columns even if empty, auto-fit collapses empty columns.

### Gap Variations

```tsx
// Tight gap
<div className="grid grid-cols-3 gap-4">

// Standard gap
<div className="grid grid-cols-3 gap-6">

// Loose gap
<div className="grid grid-cols-3 gap-8">

// Different horizontal/vertical gaps
<div className="grid grid-cols-3 gap-x-6 gap-y-12">
```

---

## Flexbox Layouts

### Centered Content

```tsx
// Center both axes
<div className="flex items-center justify-center min-h-screen">
  <div className="text-center">
    {/* Centered content */}
  </div>
</div>

// Center horizontally only
<div className="flex justify-center">
  {/* Content */}
</div>

// Center vertically only
<div className="flex items-center min-h-screen">
  {/* Content */}
</div>
```

### Space Between Layout

```tsx
// Header with logo and nav
<header className="flex items-center justify-between px-4 py-4">
  <Logo />
  <Navigation />
</header>

// Card with title and action
<div className="flex items-center justify-between p-6">
  <h3 className="text-xl font-semibold">Title</h3>
  <button>Action</button>
</div>
```

### Vertical Stack

```tsx
// Standard stack with consistent spacing
<div className="flex flex-col space-y-4">
  <Item />
  <Item />
  <Item />
</div>

// Stack with custom gaps
<div className="flex flex-col gap-6">
  <Section />
  <Section />
</div>
```

### Horizontal Row

```tsx
// Standard row
<div className="flex items-center space-x-4">
  <Icon />
  <Text />
  <Badge />
</div>

// Row with wrapping (for tags, badges)
<div className="flex flex-wrap gap-2">
  {tags.map(tag => <Badge key={tag}>{tag}</Badge>)}
</div>
```

### Responsive Flex Direction

```tsx
// Stack on mobile, row on desktop
<div className="flex flex-col lg:flex-row gap-8">
  <Sidebar />
  <MainContent />
</div>

// Row on mobile, column on desktop (rare, but possible)
<div className="flex flex-row md:flex-col gap-4">
  <Item />
  <Item />
</div>
```

---

## Two-Column Layouts

### Sidebar + Main Content

```tsx
<div className="flex flex-col lg:flex-row gap-8">
  {/* Sidebar */}
  <aside className="lg:w-64 flex-shrink-0">
    {/* Sidebar content */}
  </aside>

  {/* Main content */}
  <main className="flex-1 min-w-0">
    {/* Main content */}
  </main>
</div>
```

**Breakdown**:
- `lg:w-64` - Fixed sidebar width on desktop
- `flex-shrink-0` - Prevent sidebar from shrinking
- `flex-1` - Main content fills remaining space
- `min-w-0` - Prevent content overflow

### Reversed Sidebar (Content First on Mobile)

```tsx
<div className="flex flex-col lg:flex-row-reverse gap-8">
  {/* Sidebar (appears second on mobile) */}
  <aside className="lg:w-64 flex-shrink-0">
    {/* Sidebar content */}
  </aside>

  {/* Main content (appears first on mobile) */}
  <main className="flex-1 min-w-0">
    {/* Main content */}
  </main>
</div>
```

### Split Content (50/50)

```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
  <div>
    {/* Left content */}
  </div>
  <div>
    {/* Right content */}
  </div>
</div>
```

### Image + Text Split

```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
  <div>
    <img src="/image.jpg" alt="" className="rounded-lg" />
  </div>
  <div>
    <h2 className="text-3xl font-bold mb-4">Heading</h2>
    <p className="text-muted-foreground">Description...</p>
  </div>
</div>
```

---

## Three-Column Layouts

### Equal Columns

```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
  <div>{/* Column 1 */}</div>
  <div>{/* Column 2 */}</div>
  <div>{/* Column 3 */}</div>
</div>
```

### Sidebar + Content + Sidebar

```tsx
<div className="grid grid-cols-1 lg:grid-cols-[250px_1fr_250px] gap-8">
  <aside>{/* Left sidebar */}</aside>
  <main>{/* Main content */}</main>
  <aside>{/* Right sidebar */}</aside>
</div>
```

---

## Masonry Layout

CSS columns-based masonry (no JavaScript):

```tsx
<div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
  {items.map(item => (
    <div key={item.id} className="break-inside-avoid">
      <Card {...item} />
    </div>
  ))}
</div>
```

**When to use**: Pinterest-style layouts, image galleries, varied-height cards

---

## Sticky Positioning

### Sticky Header

```tsx
<header className="sticky top-0 z-50 w-full bg-background/95 backdrop-blur border-b">
  <div className="max-w-7xl mx-auto px-4 py-4">
    {/* Header content */}
  </div>
</header>
```

### Sticky Sidebar

```tsx
<div className="flex gap-8">
  <aside className="sticky top-4 h-fit">
    {/* Sidebar stays visible while scrolling */}
  </aside>
  <main className="flex-1">
    {/* Long scrolling content */}
  </main>
</div>
```

**Note**: `h-fit` prevents sidebar from being taller than viewport.

---

## Aspect Ratios

### Video/Image Containers

```tsx
// 16:9 aspect ratio
<div className="aspect-video">
  <iframe src="..." className="w-full h-full" />
</div>

// Square aspect ratio
<div className="aspect-square">
  <img src="..." className="w-full h-full object-cover" />
</div>

// Custom aspect ratio
<div className="aspect-[4/3]">
  <img src="..." className="w-full h-full object-cover" />
</div>
```

---

## Full-Height Layouts

### Full viewport height

```tsx
// Single section fills viewport
<section className="min-h-screen flex items-center justify-center">
  {/* Centered content */}
</section>

// Header + Content + Footer layout
<div className="min-h-screen flex flex-col">
  <header className="border-b">
    {/* Header */}
  </header>

  <main className="flex-1">
    {/* Main content grows to fill space */}
  </main>

  <footer className="border-t">
    {/* Footer */}
  </footer>
</div>
```

---

## Overflow Handling

### Horizontal Scroll

```tsx
<div className="overflow-x-auto">
  <div className="flex gap-4 pb-4">
    {items.map(item => (
      <div key={item.id} className="flex-shrink-0 w-64">
        <Card {...item} />
      </div>
    ))}
  </div>
</div>
```

### Hidden Overflow (Truncation)

```tsx
// Truncate text with ellipsis
<p className="truncate">
  Very long text that will be truncated with ellipsis...
</p>

// Multiline truncation
<p className="line-clamp-3">
  Long text that will be truncated after 3 lines with ellipsis at the end...
</p>

// Hide overflow completely
<div className="overflow-hidden">
  <Content />
</div>
```

---

## Z-Index Layers

Standard z-index scale for layering:

```tsx
// Behind content
<div className="z-0">

// Normal content
<div className="z-10">

// Dropdowns, popovers
<div className="z-20">

// Fixed elements (header, sidebar)
<div className="z-40">

// Overlays, modals
<div className="z-50">

// Tooltips
<div className="z-[60]">
```

**Best Practice**: Use increments of 10 to allow intermediate values if needed.

---

## Common Patterns Summary

| Pattern | Classes |
|---------|---------|
| **Page container** | `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` |
| **Section spacing** | `py-16 sm:py-24` |
| **Responsive grid** | `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6` |
| **Center content** | `flex items-center justify-center` |
| **Sidebar layout** | `flex flex-col lg:flex-row gap-8` |
| **Sticky header** | `sticky top-0 z-50` |
| **Full height** | `min-h-screen flex flex-col` |

---

**Related**: See `card-patterns.md` for card component layouts, `navigation-patterns.md` for header/footer patterns.
