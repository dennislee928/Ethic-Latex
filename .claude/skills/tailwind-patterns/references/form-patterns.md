# Form Patterns

Complete form styling patterns for Tailwind CSS projects.

---

## Input Fields

### Text Input

```tsx
<div className="space-y-2">
  <label htmlFor="name" className="text-sm font-medium">
    Name
  </label>
  <input
    id="name"
    type="text"
    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
    placeholder="Enter your name"
  />
</div>
```

### Email Input

```tsx
<div className="space-y-2">
  <label htmlFor="email" className="text-sm font-medium">
    Email
  </label>
  <input
    id="email"
    type="email"
    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
    placeholder="you@example.com"
  />
</div>
```

### Password Input

```tsx
<div className="space-y-2">
  <label htmlFor="password" className="text-sm font-medium">
    Password
  </label>
  <input
    id="password"
    type="password"
    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
    placeholder="••••••••"
  />
</div>
```

### Input with Helper Text

```tsx
<div className="space-y-2">
  <label htmlFor="username" className="text-sm font-medium">
    Username
  </label>
  <input
    id="username"
    type="text"
    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
  />
  <p className="text-sm text-muted-foreground">
    This will be your public display name.
  </p>
</div>
```

---

## Textarea

```tsx
<div className="space-y-2">
  <label htmlFor="message" className="text-sm font-medium">
    Message
  </label>
  <textarea
    id="message"
    rows={4}
    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
    placeholder="Type your message here..."
  />
</div>
```

---

## Select Dropdown

```tsx
<div className="space-y-2">
  <label htmlFor="country" className="text-sm font-medium">
    Country
  </label>
  <select
    id="country"
    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
  >
    <option value="">Select a country</option>
    <option value="us">United States</option>
    <option value="uk">United Kingdom</option>
    <option value="au">Australia</option>
  </select>
</div>
```

---

## Checkbox

### Single Checkbox

```tsx
<div className="flex items-center space-x-2">
  <input
    id="terms"
    type="checkbox"
    className="h-4 w-4 rounded border-border text-primary focus:ring-2 focus:ring-primary"
  />
  <label htmlFor="terms" className="text-sm">
    I agree to the terms and conditions
  </label>
</div>
```

### Checkbox Group

```tsx
<fieldset className="space-y-3">
  <legend className="text-sm font-medium mb-2">
    Preferences
  </legend>

  <div className="flex items-center space-x-2">
    <input
      id="newsletter"
      type="checkbox"
      className="h-4 w-4 rounded border-border text-primary focus:ring-2 focus:ring-primary"
    />
    <label htmlFor="newsletter" className="text-sm">
      Newsletter
    </label>
  </div>

  <div className="flex items-center space-x-2">
    <input
      id="updates"
      type="checkbox"
      className="h-4 w-4 rounded border-border text-primary focus:ring-2 focus:ring-primary"
    />
    <label htmlFor="updates" className="text-sm">
      Product updates
    </label>
  </div>
</fieldset>
```

---

## Radio Buttons

```tsx
<fieldset className="space-y-3">
  <legend className="text-sm font-medium mb-2">
    Plan
  </legend>

  <div className="flex items-center space-x-2">
    <input
      id="free"
      type="radio"
      name="plan"
      value="free"
      className="h-4 w-4 border-border text-primary focus:ring-2 focus:ring-primary"
    />
    <label htmlFor="free" className="text-sm">
      Free
    </label>
  </div>

  <div className="flex items-center space-x-2">
    <input
      id="pro"
      type="radio"
      name="plan"
      value="pro"
      className="h-4 w-4 border-border text-primary focus:ring-2 focus:ring-primary"
    />
    <label htmlFor="pro" className="text-sm">
      Pro ($29/mo)
    </label>
  </div>
</fieldset>
```

---

## Error States

### Input with Error

```tsx
<div className="space-y-2">
  <label htmlFor="email" className="text-sm font-medium">
    Email
  </label>
  <input
    id="email"
    type="email"
    className="w-full px-3 py-2 bg-background border border-destructive rounded-md focus:outline-none focus:ring-2 focus:ring-destructive"
    aria-invalid="true"
    aria-describedby="email-error"
  />
  <p id="email-error" className="text-sm text-destructive">
    Please enter a valid email address
  </p>
</div>
```

### Form with Multiple Errors

```tsx
<form className="space-y-4">
  {/* Success field */}
  <div className="space-y-2">
    <label htmlFor="username" className="text-sm font-medium">
      Username
    </label>
    <input
      id="username"
      type="text"
      className="w-full px-3 py-2 bg-background border border-success rounded-md focus:outline-none focus:ring-2 focus:ring-success"
    />
    <p className="text-sm text-success flex items-center gap-1">
      <svg className="h-4 w-4">✓</svg>
      Username is available
    </p>
  </div>

  {/* Error field */}
  <div className="space-y-2">
    <label htmlFor="email" className="text-sm font-medium">
      Email
    </label>
    <input
      id="email"
      type="email"
      className="w-full px-3 py-2 bg-background border border-destructive rounded-md focus:outline-none focus:ring-2 focus:ring-destructive"
    />
    <p className="text-sm text-destructive">
      This email is already registered
    </p>
  </div>
</form>
```

---

## Search Input

```tsx
<div className="relative">
  <input
    type="search"
    placeholder="Search..."
    className="w-full px-4 py-2 pl-10 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
  />
  <svg className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground">
    {/* Search icon */}
  </svg>
</div>
```

---

## File Upload

```tsx
<div className="space-y-2">
  <label htmlFor="file" className="text-sm font-medium">
    Upload File
  </label>
  <div className="flex items-center gap-4">
    <label
      htmlFor="file"
      className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md cursor-pointer hover:bg-secondary/80 transition-colors"
    >
      Choose File
    </label>
    <span className="text-sm text-muted-foreground">
      No file chosen
    </span>
  </div>
  <input
    id="file"
    type="file"
    className="sr-only"
  />
</div>
```

---

## Complete Form Example

```tsx
<form className="space-y-6 max-w-md">
  <div className="space-y-4">
    {/* Name */}
    <div className="space-y-2">
      <label htmlFor="name" className="text-sm font-medium">
        Name
      </label>
      <input
        id="name"
        type="text"
        className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        required
      />
    </div>

    {/* Email */}
    <div className="space-y-2">
      <label htmlFor="email" className="text-sm font-medium">
        Email
      </label>
      <input
        id="email"
        type="email"
        className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        required
      />
    </div>

    {/* Message */}
    <div className="space-y-2">
      <label htmlFor="message" className="text-sm font-medium">
        Message
      </label>
      <textarea
        id="message"
        rows={4}
        className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
        required
      />
    </div>

    {/* Terms checkbox */}
    <div className="flex items-center space-x-2">
      <input
        id="terms"
        type="checkbox"
        className="h-4 w-4 rounded border-border text-primary focus:ring-2 focus:ring-primary"
        required
      />
      <label htmlFor="terms" className="text-sm">
        I agree to the <a href="/terms" className="text-primary hover:underline">terms</a>
      </label>
    </div>
  </div>

  {/* Submit */}
  <button
    type="submit"
    className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors"
  >
    Submit
  </button>
</form>
```

---

## Best Practices

### ✅ Do

- Associate labels with inputs using `htmlFor`/`id`
- Use semantic HTML (`<form>`, `<label>`, `<fieldset>`)
- Add `focus:ring-2` for keyboard navigation visibility
- Show error messages with `aria-describedby`
- Use appropriate `type` attributes
- Include helper text when needed

### ❌ Don't

- Use placeholder as label replacement
- Skip focus states
- Forget disabled state styling
- Remove error messages after fixing
- Make required fields unclear
- Use non-semantic divs for form controls

---

**Related**: See `button-patterns.md` for submit button styling, `typography-patterns.md` for label/helper text hierarchy.
