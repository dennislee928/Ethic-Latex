# Tailwind Patterns Skill

Production-ready Tailwind CSS component patterns for building modern websites and applications.

## Auto-Trigger Keywords

This skill should be suggested when the user mentions:

**Technology Names:**
- Tailwind CSS, Tailwind, TailwindCSS
- CSS utility classes, utility-first CSS
- shadcn/ui components

**Component Types:**
- cards, card layouts, card grid
- navigation, navbar, header, footer, menu
- forms, input fields, form validation
- buttons, button variants, button styles
- grids, responsive grid, layout grid
- hero section, landing page
- typography, text styles, headings

**Layout Terms:**
- responsive design, mobile-first
- container, section padding
- flexbox, grid layout
- spacing scale, padding, margin, gap
- breakpoints, media queries

**Styling Concepts:**
- dark mode, theme switching, color tokens
- semantic colors, design tokens
- hover effects, transitions, animations
- focus states, interactive elements

**Common Issues:**
- responsive layout not working
- spacing inconsistent
- colors not dark mode compatible
- button styles not matching
- form inputs not styled
- mobile navigation broken
- grid not responsive

## What This Skill Covers

1. **Layout Patterns** - Containers, sections, responsive grids, flexbox
2. **Card Components** - Basic cards, feature cards, pricing cards, hover states
3. **Navigation** - Headers, mobile menus, footers, breadcrumbs
4. **Form Elements** - Inputs, selects, checkboxes, validation states
5. **Buttons** - All variants (primary, secondary, outline, ghost, destructive)
6. **Typography** - Responsive headings, body text, lists, badges
7. **Dark Mode** - Semantic color tokens, theme switching patterns

## Quick Example

```tsx
// Responsive feature grid with cards
<section className="py-16 sm:py-24">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {features.map(feature => (
        <div key={feature.id} className="bg-card rounded-lg border p-6 hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
          <p className="text-muted-foreground">{feature.description}</p>
        </div>
      ))}
    </div>
  </div>
</section>
```

## Related Skills

- **tailwind-v4-shadcn** - Tailwind v4 setup with shadcn/ui
- **react-hook-form-zod** - Form handling with validation
- **nextjs** - Next.js framework integration
- **cloudflare-worker-base** - Deploying Tailwind-based apps

## When to Use This Skill

Use this skill when:
- Starting a new UI component
- Building landing pages or marketing sites
- Creating forms or navigation
- Implementing responsive layouts
- Fixing dark mode compatibility
- Standardizing spacing and typography
- Converting designs to code

## Key Benefits

- Copy-paste ready components
- Mobile-first responsive patterns
- Dark mode compatible by default
- Consistent spacing and typography
- Production-tested in 10+ projects
- Semantic color tokens throughout
