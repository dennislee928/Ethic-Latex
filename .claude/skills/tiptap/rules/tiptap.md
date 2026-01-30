---
paths: "**/*.ts", "**/*.tsx", "**/editor*.ts", "**/tiptap*.ts"
---

# Tiptap v3 Corrections

Claude's training may reference Tiptap v2 patterns. This project uses **Tiptap v3**.

## SSR/Next.js: immediatelyRender Required

```typescript
/* ❌ v2 default (causes hydration mismatch in SSR) */
const editor = useEditor({
  extensions: [StarterKit],
  content: '<p>Hello</p>',
})

/* ✅ v3 SSR-safe */
const editor = useEditor({
  extensions: [StarterKit],
  content: '<p>Hello</p>',
  immediatelyRender: false, // CRITICAL for Next.js/SSR
})
```

**Error without this:** "SSR has been detected, please set `immediatelyRender` explicitly to `false`"

## Peer Dependency: @tiptap/pm Required

```bash
# ❌ Missing peer dependency (causes runtime errors)
npm install @tiptap/react @tiptap/starter-kit

# ✅ Include ProseMirror engine
npm install @tiptap/react @tiptap/starter-kit @tiptap/pm
```

## Extension Configuration (v3 Changes)

```typescript
/* ❌ v2 extension config */
StarterKit.configure({
  heading: { levels: [1, 2, 3] },
})

/* ✅ v3 extension config (same API, verify import) */
import StarterKit from '@tiptap/starter-kit'
StarterKit.configure({
  heading: { levels: [1, 2, 3] },
})
```

## Content Change Handler

```typescript
/* ❌ v2 onUpdate signature */
onUpdate: ({ editor }) => {
  const html = editor.getHTML()
}

/* ✅ v3 (same API, but check for transaction) */
onUpdate: ({ editor, transaction }) => {
  if (transaction.docChanged) {
    const html = editor.getHTML()
    onChange?.(html)
  }
}
```

## Image Extension

```typescript
/* ❌ Old import path */
import Image from '@tiptap/extension-image'

/* ✅ v3 import */
import Image from '@tiptap/extension-image'
Image.configure({
  inline: true,
  allowBase64: true, // For data URLs
})
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `useEditor({...})` without immediatelyRender | Add `immediatelyRender: false` for SSR |
| Missing @tiptap/pm | Install `@tiptap/pm` as peer dependency |
| `editor.commands.setContent()` in render | Use `useEffect` or `onUpdate` callback |
| Direct DOM manipulation | Use `editor.chain().focus().insertContent()` |
| `getHTML()` in render | Memoize or use state to avoid re-renders |
