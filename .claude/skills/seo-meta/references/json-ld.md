# JSON-LD Structured Data Reference

JSON-LD (JavaScript Object Notation for Linked Data) is Google's preferred format for structured data. It enables rich snippets, knowledge panels, and better search understanding.

## Why JSON-LD Matters

**Benefits**:
- Rich snippets in search results (stars, pricing, availability)
- Better local business display (map, hours, contact)
- Featured snippets (FAQ, How-to)
- Voice search optimization
- Knowledge Graph inclusion

**Format**: Embed in `<script type="application/ld+json">` tags in `<head>` or `<body>`.

## LocalBusiness Schema (Most Important)

Use on **homepage** and **contact page** for local businesses.

### Basic LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Acme Plumbing",
  "description": "Licensed plumbing services in Sydney",
  "@id": "https://acmeplumbing.com.au",
  "url": "https://acmeplumbing.com.au",
  "telephone": "+61-XXX-XXX-XXX",
  "email": "info@acmeplumbing.com.au",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "Sydney",
    "addressRegion": "NSW",
    "postalCode": "2000",
    "addressCountry": "AU"
  }
}
```

### Specific Business Type (Recommended)

Use specific `@type` instead of generic `LocalBusiness`:

**Trade Services**:
- `Plumber`
- `Electrician`
- `Locksmith`
- `HVACBusiness` (heating/cooling)
- `RoofingContractor`
- `GeneralContractor`

**Professional Services**:
- `Dentist`
- `Attorney`
- `Accountant`
- `FinancialService`

**Retail/Food**:
- `Restaurant`
- `Cafe`
- `Store`
- `AutoRepair`
- `BeautySalon`

**Example with Specific Type**:
```json
{
  "@context": "https://schema.org",
  "@type": "Plumber",
  "name": "Acme Plumbing",
  "description": "Licensed plumbing services in Sydney",
  "@id": "https://acmeplumbing.com.au",
  "url": "https://acmeplumbing.com.au",
  "logo": "https://acmeplumbing.com.au/logo.png",
  "image": "https://acmeplumbing.com.au/og-image.jpg",
  "telephone": "+61-XXX-XXX-XXX",
  "email": "info@acmeplumbing.com.au",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "Sydney",
    "addressRegion": "NSW",
    "postalCode": "2000",
    "addressCountry": "AU"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -33.8688,
    "longitude": 151.2093
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "07:00",
      "closes": "17:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": "Saturday",
      "opens": "08:00",
      "closes": "12:00"
    }
  ],
  "sameAs": [
    "https://facebook.com/acmeplumbing",
    "https://instagram.com/acmeplumbing",
    "https://linkedin.com/company/acmeplumbing"
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "127"
  }
}
```

### Required vs Optional Fields

**Required** (minimum viable):
- `@context`: Always `"https://schema.org"`
- `@type`: Specific business type
- `name`: Business name
- `@id`: Canonical URL
- `url`: Homepage URL
- `address`: Full postal address

**Highly Recommended**:
- `telephone`: Phone number with country code (+61)
- `email`: Contact email
- `geo`: Geographic coordinates (helps local SEO)
- `openingHoursSpecification`: Business hours
- `logo`: URL to logo image
- `image`: URL to main image

**Optional but Valuable**:
- `description`: Short business description
- `priceRange`: $ to $$$$ indicator
- `sameAs`: Social media URLs
- `aggregateRating`: Star rating and review count

## Service Schema

Use on **service pages** to describe specific services.

### Basic Service

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Hot Water Repairs",
  "description": "Fast hot water system repairs in Sydney for electric, gas, and solar systems",
  "serviceType": "Hot Water Repair",
  "provider": {
    "@type": "Plumber",
    "name": "Acme Plumbing",
    "url": "https://acmeplumbing.com.au"
  },
  "areaServed": {
    "@type": "City",
    "name": "Sydney",
    "containedInPlace": {
      "@type": "State",
      "name": "New South Wales"
    }
  },
  "availableChannel": {
    "@type": "ServiceChannel",
    "serviceUrl": "https://acmeplumbing.com.au/hot-water-repairs",
    "servicePhone": "+61-XXX-XXX-XXX"
  }
}
```

### Service with Offers

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Emergency Plumbing",
  "description": "24/7 emergency plumbing services in Sydney",
  "serviceType": "Emergency Plumbing",
  "provider": {
    "@type": "Plumber",
    "name": "Acme Plumbing",
    "url": "https://acmeplumbing.com.au"
  },
  "areaServed": {
    "@type": "City",
    "name": "Sydney"
  },
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "priceRange": "$$",
    "priceCurrency": "AUD",
    "validFrom": "2026-01-01"
  }
}
```

## FAQ Schema (Rich Snippets)

Use on pages with **FAQ sections** to get rich snippets in search results.

### Basic FAQ

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much does a plumber cost in Sydney?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Plumbing rates in Sydney typically range from $100-$150 per hour for standard work. Emergency callouts may incur higher rates. We provide upfront quotes before starting work."
      }
    },
    {
      "@type": "Question",
      "name": "Do you offer same-day service?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, we offer same-day plumbing service across Sydney for urgent repairs. Call us before 2pm for same-day availability."
      }
    },
    {
      "@type": "Question",
      "name": "Are you licensed and insured?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, all our plumbers are fully licensed by NSW Fair Trading and carry comprehensive insurance. License details are available on request."
      }
    }
  ]
}
```

**Best Practices**:
- Include 3-10 questions (most impactful)
- Use actual questions users ask (Google Search Console, customer emails)
- Keep answers 40-300 words
- Answer directly and comprehensively
- Use plain language, avoid jargon

## BreadcrumbList Schema

Use on **all pages except homepage** to show breadcrumb navigation in search results.

### Basic Breadcrumbs

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://acmeplumbing.com.au"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Services",
      "item": "https://acmeplumbing.com.au/services"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Hot Water Repairs",
      "item": "https://acmeplumbing.com.au/hot-water-repairs"
    }
  ]
}
```

**Rules**:
- Position starts at 1 (homepage)
- Each item must have unique position
- Include full URL in `item` property
- Last item is current page
- Don't include current page if it's the last crumb (optional)

## Article Schema (Blog Posts)

Use on **blog posts** for better article display in search.

### Basic Article

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "5 Signs You Need a New Hot Water System",
  "description": "Learn the warning signs that indicate it's time to replace your hot water system",
  "image": "https://acmeplumbing.com.au/images/blog/hot-water-signs.jpg",
  "author": {
    "@type": "Person",
    "name": "John Smith",
    "url": "https://acmeplumbing.com.au/about/john-smith"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Acme Plumbing",
    "logo": {
      "@type": "ImageObject",
      "url": "https://acmeplumbing.com.au/logo.png",
      "width": 600,
      "height": 60
    }
  },
  "datePublished": "2026-01-14T10:00:00+11:00",
  "dateModified": "2026-01-14T15:30:00+11:00",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://acmeplumbing.com.au/blog/5-signs-new-hot-water-system"
  }
}
```

## VideoObject Schema

Use on pages with **embedded videos**.

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "How to Fix a Leaking Tap",
  "description": "Step-by-step guide to fixing a leaking tap in under 5 minutes",
  "thumbnailUrl": "https://acmeplumbing.com.au/images/video-thumb.jpg",
  "uploadDate": "2026-01-14T10:00:00+11:00",
  "duration": "PT4M30S",
  "contentUrl": "https://acmeplumbing.com.au/videos/fix-leaking-tap.mp4",
  "embedUrl": "https://www.youtube.com/embed/VIDEO_ID"
}
```

## Review Schema

Use to display **aggregate ratings** in search results.

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Acme Plumbing",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "127",
    "bestRating": "5",
    "worstRating": "1"
  },
  "review": [
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Sarah Johnson"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5",
        "bestRating": "5"
      },
      "datePublished": "2026-01-10",
      "reviewBody": "Fast, professional service. Fixed our blocked drain within an hour. Highly recommend!"
    }
  ]
}
```

**Important**: Only include reviews you actually have. Google penalizes fake reviews.

## Multiple Schemas on One Page

You can include multiple JSON-LD blocks on a single page:

```html
<head>
  <!-- LocalBusiness -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Plumber",
    "name": "Acme Plumbing",
    ...
  }
  </script>

  <!-- Breadcrumbs -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    ...
  }
  </script>

  <!-- FAQ -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    ...
  }
  </script>
</head>
```

**Common Combinations**:
- Homepage: LocalBusiness + Review
- Service page: Service + Breadcrumbs + FAQ
- Blog post: Article + Breadcrumbs
- Contact page: LocalBusiness + Breadcrumbs

## Validation & Testing

### Google Rich Results Test

**URL**: https://search.google.com/test/rich-results

**Use Cases**:
- Test if schema is valid
- Preview how it appears in search
- Identify errors and warnings

**How to Use**:
1. Enter URL or paste code
2. Click "Test URL" or "Test Code"
3. Review results (Valid, Warnings, Errors)
4. Fix issues and retest

### Schema Markup Validator

**URL**: https://validator.schema.org

**Use Cases**:
- Validate JSON-LD syntax
- Check schema.org compliance
- More detailed validation than Google tool

### Google Search Console

**Path**: Search Console > Enhancements > [Schema Type]

**Use Cases**:
- Monitor live indexed pages with schema
- Track errors/warnings over time
- See which pages have rich results

## Common Errors

### Missing Required Fields

❌ **Error**: "Missing required field 'address'"
✅ **Fix**: Add `address` object with all required subfields

### Invalid Date Format

❌ **Wrong**: `"datePublished": "14/01/2026"`
✅ **Right**: `"datePublished": "2026-01-14T10:00:00+11:00"` (ISO 8601)

### Incorrect @type

❌ **Wrong**: `"@type": "LocalBusiness"` (too generic)
✅ **Right**: `"@type": "Plumber"` (specific)

### Missing @context

❌ **Wrong**: Missing `"@context"` field
✅ **Right**: `"@context": "https://schema.org"` (required in every schema)

### Invalid URL Format

❌ **Wrong**: Relative URLs (`/about`)
✅ **Right**: Absolute URLs (`https://example.com/about`)

## Best Practices

### Use Specific Types

Generic types don't help much:
- ❌ `LocalBusiness` → ✅ `Plumber`
- ❌ `Organization` → ✅ `ProfessionalService`
- ❌ `CreativeWork` → ✅ `Article`

### Include All Relevant Fields

Don't just use required fields. Add:
- Contact info (phone, email)
- Hours of operation
- Geographic coordinates
- Social media links
- Images and logos
- Reviews and ratings

### Keep Schema Current

Update when changes occur:
- Business hours change
- New services added
- Reviews accumulate
- Contact info updates
- Prices change

### Generate Dynamically

Don't hardcode schema:
```jsx
// Generate from CMS data
const schema = {
  "@context": "https://schema.org",
  "@type": "Service",
  "name": service.name,
  "description": service.description,
  "provider": {
    "@type": "Plumber",
    "name": business.name,
    "url": business.url
  }
};
```

### Validate Before Deploying

Always test with Google Rich Results Test before going live.

## React/Next.js Implementation

```tsx
interface ServiceSchemaProps {
  serviceName: string;
  description: string;
  areaServed: string;
  serviceUrl: string;
  phone: string;
}

export function ServiceSchema(props: ServiceSchemaProps) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": props.serviceName,
    "description": props.description,
    "serviceType": props.serviceName,
    "provider": {
      "@type": "Plumber",
      "name": "Acme Plumbing",
      "url": "https://acmeplumbing.com.au"
    },
    "areaServed": {
      "@type": "City",
      "name": props.areaServed
    },
    "availableChannel": {
      "@type": "ServiceChannel",
      "serviceUrl": props.serviceUrl,
      "servicePhone": props.phone
    }
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

## Checklist

- [ ] Valid JSON syntax (no trailing commas, proper quotes)
- [ ] `@context` is "https://schema.org"
- [ ] `@type` is specific (not generic LocalBusiness)
- [ ] All required fields present
- [ ] Absolute URLs (not relative)
- [ ] Date format is ISO 8601
- [ ] Phone includes country code (+61)
- [ ] Tested with Google Rich Results Test
- [ ] Tested with Schema Markup Validator
- [ ] No hardcoded data (generate from CMS)
- [ ] Schema matches page content

---

**Production Note**: Generate JSON-LD from database/CMS. Store templates, not hardcoded schemas.
