---
paths: "**/*.ts", "**/*.tsx", "**/*store*.ts", "**/*state*.ts"
---

# Zustand v5 Corrections

Claude's training may reference v4 patterns. This project uses **Zustand v5**.

## TypeScript: Double Parentheses Required

```typescript
/* ❌ v4 syntax (breaks middleware types) */
const useStore = create<MyState>((set) => ({
  count: 0,
  increment: () => set((s) => ({ count: s.count + 1 })),
}))

/* ✅ v5 syntax: create<T>()(...) */
const useStore = create<MyState>()((set) => ({
  count: 0,
  increment: () => set((s) => ({ count: s.count + 1 })),
}))
```

## Persist: Import from Middleware

```typescript
/* ❌ Wrong import */
import { persist, createJSONStorage } from 'zustand'

/* ✅ Import from middleware */
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

const useStore = create<MyState>()(
  persist(
    (set) => ({ /* ... */ }),
    {
      name: 'my-store',
      storage: createJSONStorage(() => localStorage),
    }
  )
)
```

## Selectors: Don't Create Objects

```typescript
/* ❌ Creates new object every render (infinite re-renders) */
const { count, increment } = useStore((s) => ({
  count: s.count,
  increment: s.increment,
}))

/* ✅ Option 1: Select separately */
const count = useStore((s) => s.count)
const increment = useStore((s) => s.increment)

/* ✅ Option 2: Use shallow comparator */
import { useShallow } from 'zustand/shallow'
const { count, increment } = useStore(
  useShallow((s) => ({ count: s.count, increment: s.increment }))
)
```

## Next.js Hydration Mismatch

```typescript
/* ❌ "Text content does not match" error */
// Persist reads localStorage on client, not server

/* ✅ Add hydration check */
interface MyState {
  count: number
  _hasHydrated: boolean
  setHasHydrated: (state: boolean) => void
}

const useStore = create<MyState>()(
  persist(
    (set) => ({
      count: 0,
      _hasHydrated: false,
      setHasHydrated: (state) => set({ _hasHydrated: state }),
    }),
    {
      name: 'my-store',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
    }
  )
)

// In component:
const hasHydrated = useStore((s) => s._hasHydrated)
if (!hasHydrated) return <Loading />
```

## Slices Pattern: Explicit Types

```typescript
/* ✅ Complex but necessary for middleware */
import { StateCreator } from 'zustand'

interface BearSlice {
  bears: number
  addBear: () => void
}

const createBearSlice: StateCreator<
  BearSlice & FishSlice, // Combined state
  [],
  [],
  BearSlice // This slice
> = (set) => ({
  bears: 0,
  addBear: () => set((s) => ({ bears: s.bears + 1 })),
})
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `create<T>((set) => ...)` | `create<T>()((set) => ...)` |
| Import persist from 'zustand' | Import from 'zustand/middleware' |
| Object in selector | Select separately or use `useShallow` |
| Next.js hydration error | Add `_hasHydrated` pattern |
| Simple slices types | Use explicit `StateCreator` types |
