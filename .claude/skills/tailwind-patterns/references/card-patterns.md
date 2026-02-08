# Card Patterns

Production-ready card component patterns for Tailwind CSS.

---

## Base Card Pattern

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  {/* Card content */}
</div>
```

**Breakdown**:
- `bg-card` - Semantic background color
- `text-card-foreground` - Text color optimized for card background
- `rounded-lg` - Rounded corners (8px)
- `border border-border` - Subtle border
- `p-6` - Internal padding (24px)

---

## Card Variants

### Basic Content Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  <h3 className="text-lg font-semibold mb-2">Card Title</h3>
  <p className="text-muted-foreground text-sm">
    Card description or supporting text goes here.
  </p>
</div>
```

### Card with Header and Footer

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border overflow-hidden">
  {/* Header */}
  <div className="px-6 py-4 border-b border-border">
    <h3 className="text-lg font-semibold">Card Title</h3>
  </div>

  {/* Body */}
  <div className="p-6">
    <p className="text-muted-foreground">Card content goes here.</p>
  </div>

  {/* Footer */}
  <div className="px-6 py-4 bg-muted border-t border-border">
    <button className="text-sm text-primary hover:underline">Learn More</button>
  </div>
</div>
```

### Card with Image

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border overflow-hidden">
  <img
    src="/image.jpg"
    alt="Card image"
    className="w-full h-48 object-cover"
  />
  <div className="p-6">
    <h3 className="text-lg font-semibold mb-2">Card Title</h3>
    <p className="text-muted-foreground text-sm">Description</p>
  </div>
</div>
```

---

## Feature Cards

### Icon Feature Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 hover:shadow-lg transition-shadow">
  {/* Icon container */}
  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
    <svg className="h-6 w-6 text-primary" /* icon path */>
      {/* Icon SVG */}
    </svg>
  </div>

  <h3 className="text-lg font-semibold mb-2">Feature Title</h3>
  <p className="text-muted-foreground text-sm">
    Feature description explaining the benefit.
  </p>
</div>
```

### Numbered Feature Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  {/* Number badge */}
  <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-semibold mb-4">
    1
  </div>

  <h3 className="text-lg font-semibold mb-2">Step One</h3>
  <p className="text-muted-foreground text-sm">
    Description of the first step in the process.
  </p>
</div>
```

### Gradient Feature Card

```tsx
<div className="relative bg-gradient-to-br from-primary/20 to-accent/20 rounded-lg border border-border p-6 overflow-hidden">
  {/* Background decoration */}
  <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-primary/10 blur-2xl" />

  <div className="relative">
    <h3 className="text-lg font-semibold mb-2">Premium Feature</h3>
    <p className="text-muted-foreground text-sm">
      Standout feature with gradient background.
    </p>
  </div>
</div>
```

---

## Stat Cards

### Simple Stat Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  <div className="text-sm text-muted-foreground mb-1">Total Users</div>
  <div className="text-3xl font-bold">12,345</div>
  <div className="text-sm text-success flex items-center mt-2">
    <svg className="h-4 w-4 mr-1">↑</svg>
    <span>12% from last month</span>
  </div>
</div>
```

### Stat Card with Icon

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  <div className="flex items-center justify-between mb-4">
    <div className="text-sm text-muted-foreground">Revenue</div>
    <div className="h-10 w-10 rounded-full bg-success/10 flex items-center justify-center">
      <svg className="h-5 w-5 text-success">💰</svg>
    </div>
  </div>
  <div className="text-2xl font-bold">$45,231</div>
  <div className="text-sm text-muted-foreground mt-1">+20.1% from last month</div>
</div>
```

---

## Pricing Cards

### Basic Pricing Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-8">
  {/* Plan name */}
  <div className="text-sm font-semibold text-primary mb-2">Starter</div>

  {/* Price */}
  <div className="mb-6">
    <span className="text-4xl font-bold">$19</span>
    <span className="text-muted-foreground">/month</span>
  </div>

  {/* Description */}
  <p className="text-sm text-muted-foreground mb-6">
    Perfect for small teams getting started.
  </p>

  {/* CTA */}
  <button className="w-full bg-primary text-primary-foreground py-2 px-4 rounded-md hover:bg-primary/90 transition-colors">
    Get Started
  </button>

  {/* Features */}
  <ul className="mt-6 space-y-3">
    <li className="flex items-start text-sm">
      <svg className="h-5 w-5 text-primary mr-2 flex-shrink-0">✓</svg>
      <span>Up to 10 users</span>
    </li>
    <li className="flex items-start text-sm">
      <svg className="h-5 w-5 text-primary mr-2 flex-shrink-0">✓</svg>
      <span>5GB storage</span>
    </li>
    <li className="flex items-start text-sm">
      <svg className="h-5 w-5 text-primary mr-2 flex-shrink-0">✓</svg>
      <span>Email support</span>
    </li>
  </ul>
</div>
```

### Featured Pricing Card (Recommended)

```tsx
<div className="bg-card text-card-foreground rounded-lg border-2 border-primary p-8 relative shadow-lg">
  {/* Popular badge */}
  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
    <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
      Most Popular
    </span>
  </div>

  {/* Plan name */}
  <div className="text-sm font-semibold text-primary mb-2">Pro</div>

  {/* Price */}
  <div className="mb-6">
    <span className="text-4xl font-bold">$49</span>
    <span className="text-muted-foreground">/month</span>
  </div>

  {/* Description */}
  <p className="text-sm text-muted-foreground mb-6">
    For growing teams that need more power.
  </p>

  {/* CTA */}
  <button className="w-full bg-primary text-primary-foreground py-2 px-4 rounded-md hover:bg-primary/90 transition-colors">
    Get Started
  </button>

  {/* Features */}
  <ul className="mt-6 space-y-3">
    <li className="flex items-start text-sm">
      <svg className="h-5 w-5 text-primary mr-2 flex-shrink-0">✓</svg>
      <span>Unlimited users</span>
    </li>
    <li className="flex items-start text-sm">
      <svg className="h-5 w-5 text-primary mr-2 flex-shrink-0">✓</svg>
      <span>50GB storage</span>
    </li>
    <li className="flex items-start text-sm">
      <svg className="h-5 w-5 text-primary mr-2 flex-shrink-0">✓</svg>
      <span>Priority support</span>
    </li>
    <li className="flex items-start text-sm">
      <svg className="h-5 w-5 text-primary mr-2 flex-shrink-0">✓</svg>
      <span>Advanced analytics</span>
    </li>
  </ul>
</div>
```

---

## Testimonial Cards

### Simple Testimonial

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  <p className="text-muted-foreground mb-4">
    "This product has completely transformed how we work. Highly recommended!"
  </p>
  <div className="flex items-center">
    <img
      src="/avatar.jpg"
      alt="Sarah Johnson"
      className="h-10 w-10 rounded-full mr-3"
    />
    <div>
      <div className="font-semibold text-sm">Sarah Johnson</div>
      <div className="text-muted-foreground text-xs">CEO, TechCorp</div>
    </div>
  </div>
</div>
```

### Testimonial with Rating

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  {/* Star rating */}
  <div className="flex gap-1 mb-4">
    {[...Array(5)].map((_, i) => (
      <svg key={i} className="h-5 w-5 text-yellow-400 fill-current">⭐</svg>
    ))}
  </div>

  <p className="text-muted-foreground mb-4">
    "Exceptional quality and outstanding support. Worth every penny."
  </p>

  <div className="flex items-center">
    <img
      src="/avatar.jpg"
      alt="John Smith"
      className="h-10 w-10 rounded-full mr-3"
    />
    <div>
      <div className="font-semibold text-sm">John Smith</div>
      <div className="text-muted-foreground text-xs">Founder, StartupCo</div>
    </div>
  </div>
</div>
```

---

## Product Cards

### E-commerce Product Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border overflow-hidden group">
  {/* Image */}
  <div className="relative aspect-square overflow-hidden bg-muted">
    <img
      src="/product.jpg"
      alt="Product name"
      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
    />
    {/* Badge */}
    <div className="absolute top-2 right-2">
      <span className="bg-destructive text-destructive-foreground text-xs font-semibold px-2 py-1 rounded">
        -20%
      </span>
    </div>
  </div>

  {/* Content */}
  <div className="p-4">
    <h3 className="font-semibold mb-1">Product Name</h3>
    <p className="text-sm text-muted-foreground mb-3">Short description</p>

    {/* Price */}
    <div className="flex items-center justify-between">
      <div>
        <span className="text-lg font-bold">$79</span>
        <span className="text-sm text-muted-foreground line-through ml-2">$99</span>
      </div>
      <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm hover:bg-primary/90">
        Add to Cart
      </button>
    </div>
  </div>
</div>
```

---

## Blog Post Cards

### Horizontal Blog Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border overflow-hidden flex flex-col md:flex-row">
  {/* Image */}
  <div className="md:w-1/3">
    <img
      src="/blog-post.jpg"
      alt="Post title"
      className="w-full h-48 md:h-full object-cover"
    />
  </div>

  {/* Content */}
  <div className="p-6 md:w-2/3">
    {/* Category */}
    <div className="text-xs font-semibold text-primary mb-2">Technology</div>

    {/* Title */}
    <h3 className="text-xl font-bold mb-2">
      10 Tips for Better Web Development
    </h3>

    {/* Excerpt */}
    <p className="text-muted-foreground text-sm mb-4">
      Learn the essential techniques that will make you a more effective developer...
    </p>

    {/* Meta */}
    <div className="flex items-center text-sm text-muted-foreground">
      <span>By John Doe</span>
      <span className="mx-2">•</span>
      <span>5 min read</span>
      <span className="mx-2">•</span>
      <span>Jan 14, 2026</span>
    </div>
  </div>
</div>
```

### Vertical Blog Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border overflow-hidden">
  {/* Image */}
  <img
    src="/blog-post.jpg"
    alt="Post title"
    className="w-full h-48 object-cover"
  />

  {/* Content */}
  <div className="p-6">
    {/* Category */}
    <div className="text-xs font-semibold text-primary mb-2">Design</div>

    {/* Title */}
    <h3 className="text-lg font-bold mb-2">
      Mastering Modern UI Design
    </h3>

    {/* Excerpt */}
    <p className="text-muted-foreground text-sm mb-4">
      Explore the principles of creating beautiful, functional interfaces...
    </p>

    {/* Meta */}
    <div className="flex items-center text-sm text-muted-foreground">
      <img src="/author.jpg" alt="Author" className="h-6 w-6 rounded-full mr-2" />
      <span>Jane Smith</span>
      <span className="mx-2">•</span>
      <span>8 min read</span>
    </div>
  </div>
</div>
```

---

## Interactive States

### Hover Lift Effect

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 transition-transform hover:scale-105">
  {/* Card content */}
</div>
```

### Hover Shadow

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 transition-shadow hover:shadow-lg">
  {/* Card content */}
</div>
```

### Hover Border Color

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 transition-colors hover:border-primary">
  {/* Card content */}
</div>
```

### Combined Hover Effects

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 transition-all hover:shadow-lg hover:border-primary hover:-translate-y-1">
  {/* Card content */}
</div>
```

### Active/Selected State

```tsx
<div className="bg-card text-card-foreground rounded-lg border-2 border-primary p-6 shadow-lg ring-2 ring-primary/20">
  {/* Selected card content */}
</div>
```

---

## Loading States

### Skeleton Card

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6 animate-pulse">
  <div className="h-12 w-12 bg-muted rounded-lg mb-4" />
  <div className="h-4 bg-muted rounded w-3/4 mb-2" />
  <div className="h-3 bg-muted rounded w-full mb-1" />
  <div className="h-3 bg-muted rounded w-5/6" />
</div>
```

---

## Responsive Card Grids

```tsx
{/* 1 column mobile, 2 tablet, 3 desktop */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {cards.map(card => <Card key={card.id} {...card} />)}
</div>

{/* 2 columns mobile, 3 tablet, 4 desktop */}
<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
  {cards.map(card => <Card key={card.id} {...card} />)}
</div>
```

---

## Card Best Practices

### ✅ Do

- Use semantic colors (`bg-card`, `text-card-foreground`)
- Add subtle transitions on interactive cards
- Maintain consistent padding (p-6 standard)
- Use `overflow-hidden` when images touch edges
- Include hover states for clickable cards
- Keep card content hierarchy clear

### ❌ Don't

- Use raw colors like `bg-white` or `bg-gray-100`
- Add excessive shadows (subtle is better)
- Make non-clickable cards look interactive
- Overflow content without truncation
- Mix border and shadow styles randomly
- Forget responsive image sizing

---

**Related**: See `layout-patterns.md` for card grid layouts, `typography-patterns.md` for card text hierarchy.
