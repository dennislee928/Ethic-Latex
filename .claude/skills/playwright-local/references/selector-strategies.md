# Playwright Selector Strategies

Guide to choosing the right selector strategy for reliable automation.

## Selector Types

| Type | Example | Pros | Cons |
|------|---------|------|------|
| **CSS** | `button.submit` | Fast, standard | Breaks with class changes |
| **XPath** | `//button[text()="Submit"]` | Flexible, text-based | Slower, verbose |
| **Text** | `text=Submit` | Resilient to structure | Fails with text changes |
| **Data attributes** | `[data-testid="submit"]` | Stable, semantic | Requires dev cooperation |
| **Role** | `role=button[name="Submit"]` | Accessible, semantic | Limited browser support |
| **Nth child** | `li:nth-child(2)` | Position-based | Fragile (order changes) |

## Selector Hierarchy (Best to Worst)

1. **data-testid** (most stable)
2. **ID** (if unique and semantic)
3. **Text content** (if stable)
4. **CSS class** (if semantic)
5. **XPath** (as fallback)
6. **Nth-child** (last resort)

## CSS Selectors

### Basic

```typescript
await page.click('button'); // Tag
await page.click('#submit'); // ID
await page.click('.btn-primary'); // Class
await page.click('[type="submit"]'); // Attribute
```

### Combinators

```typescript
await page.click('form > button'); // Child
await page.click('form button'); // Descendant
await page.click('label + input'); // Adjacent sibling
await page.click('h2 ~ p'); // General sibling
```

### Pseudo-classes

```typescript
await page.click('button:first-child');
await page.click('button:last-child');
await page.click('button:nth-child(2)');
await page.click('input:checked');
await page.click('input:disabled');
await page.click('a:visited');
```

### Attribute selectors

```typescript
await page.click('[href^="https"]'); // Starts with
await page.click('[href$=".pdf"]'); // Ends with
await page.click('[href*="example"]'); // Contains
await page.click('[data-id="123"]'); // Exact match
```

## XPath Selectors

Prefix with `xpath=`:

```typescript
// Text matching
await page.click('xpath=//button[text()="Submit"]');
await page.click('xpath=//button[contains(text(), "Sub")]');

// Attributes
await page.click('xpath=//button[@class="submit"]');
await page.click('xpath=//button[contains(@class, "submit")]');

// Hierarchy
await page.click('xpath=//form//button'); // Descendant
await page.click('xpath=//form/button'); // Child

// Position
await page.click('xpath=(//button)[1]'); // First
await page.click('xpath=(//button)[last()]'); // Last

// Combinations
await page.click('xpath=//button[@type="submit" and contains(text(), "Save")]');
```

## Text Selectors

```typescript
// Exact match
await page.click('text=Submit');

// Substring
await page.click('text="Submit form"'); // Full string

// Case-insensitive
await page.click('text=/submit/i');

// Regex
await page.click('text=/^Submit/');
```

## Playwright-specific Selectors

### has-text

```typescript
await page.click('button:has-text("Submit")');
await page.click('article:has-text("Breaking News")');
```

### has (selector within)

```typescript
await page.click('article:has(img.thumbnail)');
await page.click('div:has(> button.primary)');
```

### is (filter)

```typescript
await page.click('button:is(.submit, .confirm)');
```

### not (exclude)

```typescript
await page.click('button:not(.disabled)');
```

## Chaining Selectors

Playwright supports chaining for complex queries:

```typescript
// Find article, then find button inside it
await page.locator('article').locator('button.submit').click();

// Filter by text, then find child
await page.locator('div:has-text("Settings")').locator('button').click();
```

## Best Practices

### 1. Prefer data-testid

Ask devs to add:
```html
<button data-testid="submit-form">Submit</button>
```

Then:
```typescript
await page.click('[data-testid="submit-form"]');
```

### 2. Use getByRole for Accessibility

```typescript
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
```

### 3. Combine Strategies

```typescript
// Text within specific context
await page.locator('form.login').getByText('Submit').click();

// Role within section
await page.locator('section.checkout').getByRole('button', { name: 'Pay' }).click();
```

### 4. Use nth for Lists

```typescript
// Get 3rd item in list
await page.locator('.product-card').nth(2).click();

// Get first/last
await page.locator('.product-card').first().click();
await page.locator('.product-card').last().click();
```

## Debugging Selectors

### Count matches

```typescript
const count = await page.locator('button').count();
console.log(`Found ${count} buttons`);
```

### Get all matching elements

```typescript
const elements = await page.locator('.item').all();
for (const el of elements) {
  console.log(await el.textContent());
}
```

### Use Playwright Inspector

```bash
PWDEBUG=1 npx playwright test
```

This opens visual inspector to test selectors.

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Selector finds multiple | Not specific enough | Add parent context or unique attribute |
| Element not found | Wrong selector or timing | Use `waitForSelector()` first |
| Stale element | DOM re-rendered | Re-query after navigation |
| Slow selectors | Complex XPath | Simplify or use CSS |
| Flaky tests | Timing issues | Add explicit waits |

## Dynamic Content

For content that loads dynamically:

```typescript
// Wait for selector
await page.waitForSelector('.loaded-content');

// Or use auto-waiting locator
await page.locator('.loaded-content').click(); // Waits automatically
```

## Shadow DOM

Playwright pierces shadow DOM automatically:

```typescript
// Works even in shadow root
await page.click('custom-element .shadow-button');
```

## Performance Tips

| Selector | Speed | Notes |
|----------|-------|-------|
| ID | Fastest | Browser-native |
| Class | Fast | Browser-native |
| Tag | Fast | Browser-native |
| XPath | Slower | Parsed by Playwright |
| Text | Slower | Must traverse text nodes |

For high-volume scraping, prefer CSS selectors.
