# {{PROJECT_NAME}}

**Last Updated**: {{DATE}}

---

## Project Overview

{{DESCRIPTION}}

**Tech Stack**: Next.js (App Router), {{TECH_STACK}}

---

## Quick Start

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

---

## Development

### Local Development

```bash
pnpm dev              # Start Next.js dev server (http://localhost:3000)
```

### Build & Deploy

```bash
pnpm build            # Build for production
pnpm start            # Start production server locally
```

Deployment is typically automatic via Vercel on git push.

---

## Project Structure

```
app/
├── layout.tsx        # Root layout
├── page.tsx          # Home page
├── globals.css       # Global styles
├── (routes)/         # Route groups
│   ├── dashboard/    # Dashboard pages
│   └── api/          # API routes
└── components/       # Shared components

lib/
├── db.ts             # Database client
├── auth.ts           # Authentication
└── utils.ts          # Utility functions

public/               # Static assets
```

---

## App Router Conventions

### Route Files

| File | Purpose |
|------|---------|
| `page.tsx` | Page component (required for route) |
| `layout.tsx` | Shared layout |
| `loading.tsx` | Loading UI |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |

### Server vs Client Components

```tsx
// Server Component (default)
export default async function Page() {
  const data = await fetchData(); // Can use async/await
  return <div>{data}</div>;
}

// Client Component
'use client';
export default function Button() {
  const [state, setState] = useState(); // Can use hooks
  return <button onClick={() => {}}>{state}</button>;
}
```

---

## Environment Variables

### Local Development (.env.local)

```bash
# Database
DATABASE_URL="..."

# Authentication
AUTH_SECRET="..."

# API Keys
NEXT_PUBLIC_API_URL="..."  # Exposed to client
```

### Production (Vercel)

Set in Vercel Dashboard → Project → Settings → Environment Variables

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

---

## Key Files

| File | Purpose |
|------|---------|
| `next.config.ts` | Next.js configuration |
| `app/layout.tsx` | Root layout |
| `app/page.tsx` | Home page |
| `middleware.ts` | Request middleware |
| `tailwind.config.ts` | Tailwind configuration |

---

## Common Tasks

### Add a New Page

1. Create folder in `app/` matching the route
2. Add `page.tsx` file
3. Optionally add `layout.tsx`, `loading.tsx`, `error.tsx`

### Add an API Route

1. Create `app/api/[name]/route.ts`
2. Export route handlers:

```typescript
export async function GET(request: Request) {
  return Response.json({ data: 'value' });
}

export async function POST(request: Request) {
  const body = await request.json();
  return Response.json({ received: body });
}
```

### Add Server Action

```typescript
'use server';

export async function submitForm(formData: FormData) {
  const name = formData.get('name');
  // Process and return result
  return { success: true };
}
```

---

## Data Fetching

### Server Component (Recommended)

```typescript
export default async function Page() {
  // This runs on the server
  const data = await db.query.table.findMany();
  return <Component data={data} />;
}
```

### Client-Side (When Needed)

```typescript
'use client';
import useSWR from 'swr';

export default function Page() {
  const { data, error } = useSWR('/api/data', fetcher);
  if (error) return <Error />;
  if (!data) return <Loading />;
  return <Component data={data} />;
}
```

---

## Authentication

<!-- Customize based on auth solution (Clerk, NextAuth, etc.) -->

### Protected Routes

Use middleware or layout checks:

```typescript
// middleware.ts
export function middleware(request: Request) {
  const session = getSession(request);
  if (!session) {
    return NextResponse.redirect('/login');
  }
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*'],
};
```

---

## Troubleshooting

### Hydration Errors
- Check for client-only code in Server Components
- Ensure consistent rendering between server and client
- Use `suppressHydrationWarning` for intentional differences

### Build Errors
- Check for dynamic code in static context
- Verify all environment variables are set

### 404 on API Routes
- Ensure route file exports HTTP method handlers
- Check route file is named `route.ts` (not `page.tsx`)
