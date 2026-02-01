---
paths: "**/*.ts", "**/*.tsx", "**/route*.ts", "**/router*.ts"
---

# TanStack Router v1 Corrections

Claude's training may have limited TanStack Router knowledge. This project uses **TanStack Router v1**.

## File-Based Routing (Recommended)

```typescript
/* ❌ Manual route definitions (verbose) */
const router = createRouter({
  routeTree: rootRoute.addChildren([
    indexRoute,
    aboutRoute,
  ]),
})

/* ✅ File-based routing with routeTree.gen.ts */
// routes/__root.tsx, routes/index.tsx, routes/about.tsx
// Then import generated tree:
import { routeTree } from './routeTree.gen'
const router = createRouter({ routeTree })
```

## Route File Structure

```typescript
/* ❌ Wrong file naming */
// routes/About.tsx - capitalized won't work
// routes/about/page.tsx - Next.js convention

/* ✅ TanStack Router conventions */
// routes/__root.tsx - root layout
// routes/index.tsx - home page (/)
// routes/about.tsx - /about
// routes/posts/$postId.tsx - /posts/:postId (dynamic)
// routes/posts/index.tsx - /posts
```

## createFileRoute vs createRoute

```typescript
/* ❌ Using createRoute in file-based routing */
import { createRoute } from '@tanstack/react-router'
const Route = createRoute({...})

/* ✅ Use createFileRoute for file-based */
import { createFileRoute } from '@tanstack/react-router'
export const Route = createFileRoute('/about')({
  component: AboutPage,
})
```

## Loader Pattern

```typescript
/* ❌ React Router style loader */
export async function loader({ params }) {
  return fetch(`/api/posts/${params.id}`)
}

/* ✅ TanStack Router loader */
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => {
    return fetchPost(params.postId)
  },
  component: PostPage,
})

function PostPage() {
  const post = Route.useLoaderData()
  return <div>{post.title}</div>
}
```

## Search Params

```typescript
/* ❌ Manual URLSearchParams */
const params = new URLSearchParams(window.location.search)

/* ✅ Type-safe search params */
export const Route = createFileRoute('/search')({
  validateSearch: (search) => ({
    q: search.q as string || '',
    page: Number(search.page) || 1,
  }),
})

function SearchPage() {
  const { q, page } = Route.useSearch()
}
```

## Navigation

```typescript
/* ❌ useNavigate like React Router */
import { useNavigate } from 'react-router-dom'
const navigate = useNavigate()
navigate('/about')

/* ✅ TanStack Router navigation */
import { useNavigate, Link } from '@tanstack/react-router'
const navigate = useNavigate()
navigate({ to: '/about' })

// Or type-safe Link
<Link to="/posts/$postId" params={{ postId: '123' }}>
  View Post
</Link>
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `createRoute` in file-based | `createFileRoute` |
| `routes/About.tsx` | `routes/about.tsx` (lowercase) |
| `loader({ params })` export | `loader` inside `createFileRoute` |
| `useParams()` | `Route.useParams()` |
| `useSearchParams()` | `Route.useSearch()` with `validateSearch` |
| `navigate('/path')` | `navigate({ to: '/path' })` |
