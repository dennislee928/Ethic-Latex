# Icon Templates

Ready-to-use patterns for common icon layouts using Tailwind v4 semantic colours.

## Feature Card Icon (Rounded Square)

```tsx
import { Trophy } from 'lucide-react'

<div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center">
  <Trophy className="w-8 h-8 text-primary" />
</div>
```

**Heroicons variant:**
```tsx
import { TrophyIcon } from '@heroicons/react/24/outline'

<div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center">
  <TrophyIcon className="w-8 h-8 text-primary" />
</div>
```

## Feature Card Icon (Circle)

```tsx
import { Shield } from 'lucide-react'

<div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
  <Shield className="w-6 h-6 text-primary" />
</div>
```

## Inline Icon (Contact Info)

```tsx
import { Phone, Mail, MapPin } from 'lucide-react'

<span className="inline-flex items-center gap-2 text-muted-foreground">
  <Phone className="w-4 h-4" />
  <span>1300 123 456</span>
</span>

<span className="inline-flex items-center gap-2 text-muted-foreground">
  <Mail className="w-4 h-4" />
  <span>hello@example.com</span>
</span>

<span className="inline-flex items-center gap-2 text-muted-foreground">
  <MapPin className="w-4 h-4" />
  <span>Sydney, Australia</span>
</span>
```

## List Item with Icon

```tsx
import { Check } from 'lucide-react'

<ul className="space-y-3">
  <li className="flex items-start gap-3">
    <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
    <span>First benefit or feature</span>
  </li>
  <li className="flex items-start gap-3">
    <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
    <span>Second benefit or feature</span>
  </li>
</ul>
```

## Button with Icon

```tsx
import { ArrowRight } from 'lucide-react'

// Primary button
<button className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
  <span>Get Started</span>
  <ArrowRight className="w-4 h-4" />
</button>

// Secondary/outline button
<button className="inline-flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted">
  <span>Learn More</span>
  <ArrowRight className="w-4 h-4" />
</button>
```

## Icon-Only Button

```tsx
import { Menu, X, Search } from 'lucide-react'

// Mobile menu toggle
<button
  className="p-2 rounded-lg hover:bg-muted transition-colors"
  aria-label="Open menu"
>
  <Menu className="w-6 h-6" />
</button>

// Close button
<button
  className="p-2 rounded-lg hover:bg-muted transition-colors"
  aria-label="Close"
>
  <X className="w-5 h-5" />
</button>

// Search button
<button
  className="p-2 rounded-lg hover:bg-muted transition-colors"
  aria-label="Search"
>
  <Search className="w-5 h-5" />
</button>
```

## Feature Grid Card

```tsx
import { Shield, Zap, Users, Trophy } from 'lucide-react'

const features = [
  { icon: Shield, title: 'Secure', description: 'Enterprise-grade security' },
  { icon: Zap, title: 'Fast', description: 'Lightning quick response' },
  { icon: Users, title: 'Support', description: '24/7 expert help' },
  { icon: Trophy, title: 'Award-Winning', description: 'Industry recognized' },
]

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {features.map(({ icon: Icon, title, description }) => (
    <div key={title} className="p-6 rounded-xl bg-card border border-border">
      <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
        <Icon className="w-6 h-6 text-primary" />
      </div>
      <h3 className="font-semibold text-card-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  ))}
</div>
```

## Status Badge with Icon

```tsx
import { CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react'

// Success
<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 text-green-600 text-sm">
  <CheckCircle className="w-4 h-4" />
  <span>Active</span>
</span>

// Error
<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-destructive/10 text-destructive text-sm">
  <XCircle className="w-4 h-4" />
  <span>Failed</span>
</span>

// Warning
<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-500/10 text-yellow-600 text-sm">
  <AlertTriangle className="w-4 h-4" />
  <span>Warning</span>
</span>

// Pending
<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-muted text-muted-foreground text-sm">
  <Clock className="w-4 h-4" />
  <span>Pending</span>
</span>
```

## Navigation Item

```tsx
import { Home, Users, Settings, type LucideIcon } from 'lucide-react'

interface NavItemProps {
  icon: LucideIcon
  label: string
  href: string
  active?: boolean
}

function NavItem({ icon: Icon, label, href, active }: NavItemProps) {
  return (
    <a
      href={href}
      className={cn(
        'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
        active
          ? 'bg-primary/10 text-primary'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      )}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
    </a>
  )
}
```

## Input with Icon

```tsx
import { Search, Mail } from 'lucide-react'

// Search input
<div className="relative">
  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
  <input
    type="text"
    placeholder="Search..."
    className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
  />
</div>

// Email input
<div className="relative">
  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
  <input
    type="email"
    placeholder="Enter your email"
    className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
  />
</div>
```

---

## Colour Reference

All templates use Tailwind v4 semantic tokens:

| Token | Use |
|-------|-----|
| `text-primary` | Icon accent colour |
| `bg-primary/10` | Icon background (10% opacity) |
| `text-muted-foreground` | Secondary/subtle icons |
| `text-foreground` | Default icon colour |
| `text-card-foreground` | Icons on card backgrounds |
| `text-destructive` | Error/delete icons |

**Never use raw colours** like `text-blue-500` - always use semantic tokens.
