# Typography Patterns

Text hierarchy and typography patterns for Tailwind CSS projects.

---

## Headings

### Responsive Headings

```tsx
// H1 - Page title
<h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold">
  Page Title
</h1>

// H2 - Section title
<h2 className="text-3xl sm:text-4xl font-bold">
  Section Title
</h2>

// H3 - Subsection
<h3 className="text-2xl sm:text-3xl font-semibold">
  Subsection
</h3>

// H4 - Card/component title
<h4 className="text-xl font-semibold">
  Component Title
</h4>

// H5 - Small headings
<h5 className="text-lg font-semibold">
  Small Heading
</h5>

// H6 - Micro headings
<h6 className="text-base font-semibold">
  Micro Heading
</h6>
```

### Heading with Subtitle

```tsx
<div>
  <h2 className="text-3xl font-bold mb-2">
    Main Heading
  </h2>
  <p className="text-lg text-muted-foreground">
    Supporting subtitle or description
  </p>
</div>
```

---

## Body Text

### Paragraph Sizes

```tsx
// Large paragraph (intros, lead text)
<p className="text-lg text-muted-foreground leading-relaxed">
  Larger body text with comfortable line height for better readability.
</p>

// Standard paragraph
<p className="text-base text-muted-foreground">
  Regular paragraph text for body content.
</p>

// Small paragraph (captions, footnotes)
<p className="text-sm text-muted-foreground">
  Small supporting text or captions.
</p>

// Extra small (labels, metadata)
<p className="text-xs text-muted-foreground">
  Very small text for labels or metadata.
</p>
```

### Text Colors

```tsx
// Primary foreground (default)
<p className="text-foreground">
  Standard text color
</p>

// Muted (secondary text)
<p className="text-muted-foreground">
  Secondary or supporting text
</p>

// Primary accent
<p className="text-primary">
  Highlighted or accent text
</p>

// Success/Warning/Destructive
<p className="text-success">Success message</p>
<p className="text-warning">Warning message</p>
<p className="text-destructive">Error message</p>
```

---

## Lists

### Unordered List

```tsx
<ul className="space-y-2 text-muted-foreground">
  <li>First item</li>
  <li>Second item</li>
  <li>Third item</li>
</ul>
```

### List with Icons

```tsx
<ul className="space-y-3">
  <li className="flex items-start">
    <svg className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0">✓</svg>
    <span className="text-muted-foreground">Feature one with longer description</span>
  </li>
  <li className="flex items-start">
    <svg className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0">✓</svg>
    <span className="text-muted-foreground">Feature two</span>
  </li>
</ul>
```

### Ordered List

```tsx
<ol className="space-y-2 text-muted-foreground list-decimal list-inside">
  <li>First step</li>
  <li>Second step</li>
  <li>Third step</li>
</ol>
```

---

## Links

### Inline Link

```tsx
<p>
  This is a paragraph with an{' '}
  <a href="#" className="text-primary hover:underline underline-offset-4">
    inline link
  </a>
  {' '}in the middle.
</p>
```

### Standalone Link

```tsx
<a
  href="#"
  className="text-primary hover:text-primary/80 underline underline-offset-4 transition-colors"
>
  Standalone link
</a>
```

### Link with Icon

```tsx
<a
  href="#"
  className="inline-flex items-center gap-1 text-primary hover:underline underline-offset-4"
>
  <span>Learn more</span>
  <svg className="h-4 w-4">→</svg>
</a>
```

---

## Blockquote

```tsx
<blockquote className="border-l-4 border-primary pl-4 italic text-muted-foreground">
  "This is a quote that provides emphasis or attribution to a statement."
  <footer className="mt-2 text-sm not-italic">
    — Author Name
  </footer>
</blockquote>
```

---

## Code Blocks

### Inline Code

```tsx
<p>
  Use the <code className="px-1.5 py-0.5 bg-muted rounded text-sm font-mono">className</code> attribute.
</p>
```

### Code Block

```tsx
<pre className="bg-muted p-4 rounded-lg overflow-x-auto">
  <code className="text-sm font-mono">
{`function hello() {
  console.log("Hello World");
}`}
  </code>
</pre>
```

---

## Badges

### Status Badges

```tsx
// Success
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success">
  Active
</span>

// Warning
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning/10 text-warning">
  Pending
</span>

// Destructive
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-destructive/10 text-destructive">
  Error
</span>

// Neutral
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-muted text-muted-foreground">
  Draft
</span>
```

### Count Badge

```tsx
<button className="relative">
  Notifications
  <span className="absolute -top-1 -right-1 h-5 w-5 bg-destructive text-destructive-foreground rounded-full text-xs flex items-center justify-center">
    3
  </span>
</button>
```

---

## Text Utilities

### Truncation

```tsx
// Single line truncate
<p className="truncate max-w-xs">
  Very long text that will be truncated with ellipsis if it exceeds the width
</p>

// Multi-line clamp (3 lines)
<p className="line-clamp-3">
  Long text that will be truncated after three lines with an ellipsis at the end of the third line
</p>
```

### Text Alignment

```tsx
<p className="text-left">Left aligned</p>
<p className="text-center">Center aligned</p>
<p className="text-right">Right aligned</p>
<p className="text-justify">Justified text</p>
```

### Font Weights

```tsx
<p className="font-light">Light text (300)</p>
<p className="font-normal">Normal text (400)</p>
<p className="font-medium">Medium text (500)</p>
<p className="font-semibold">Semibold text (600)</p>
<p className="font-bold">Bold text (700)</p>
```

---

## Prose Content (Blog Posts, Markdown)

For long-form content, use `@tailwindcss/typography` plugin:

```tsx
<article className="prose prose-slate dark:prose-invert max-w-none">
  <h1>Article Title</h1>
  <p>Article content with automatic typography styles...</p>
  <h2>Section</h2>
  <p>More content...</p>
</article>
```

---

## Best Practices

### ✅ Do

- Use semantic HTML (`<h1>`, `<p>`, `<strong>`)
- Follow heading hierarchy (h1 → h2 → h3)
- Use muted colors for body text
- Add line-height utilities for readability
- Use responsive text sizes (`text-4xl sm:text-5xl`)
- Maintain consistent spacing between elements

### ❌ Don't

- Skip heading levels (h1 → h3)
- Use same size for all headings
- Forget responsive text sizing
- Use `<div>` instead of `<p>` for paragraphs
- Make body text too dark (reduces readability)
- Use fixed px values for text

---

**Related**: See `card-patterns.md` for card text hierarchy, `form-patterns.md` for label styling.
