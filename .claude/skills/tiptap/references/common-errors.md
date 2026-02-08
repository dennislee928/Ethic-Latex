# Tiptap Common Errors & Solutions

**Last Updated**: 2025-11-29

This reference documents common Tiptap errors with proven solutions.

---

## Error #1: SSR Hydration Mismatch

### Error Message
```
Warning: Prop `dangerouslySetInnerHTML` did not match. Server: "..." Client: "..."

or

SSR has been detected, please set `immediatelyRender` explicitly to `false` to avoid hydration mismatches.
```

### Stack Trace Example
```
at EditorContent
at Editor
at App
at ServerRoot
```

### Why It Happens
- Tiptap v3 defaults to `immediatelyRender: true`
- This causes editor to render on server AND client
- Server HTML doesn't match client-rendered HTML
- Results in React hydration mismatch

### Solution
Always set `immediatelyRender: false` in Next.js/SSR apps:

```typescript
const editor = useEditor({
  extensions: [StarterKit],
  immediatelyRender: false, // ⚠️ Required for SSR
  // ... other options
})
```

### References
- GitHub Issue: https://github.com/ueberdosis/tiptap/issues/5856
- GitHub Issue: https://github.com/ueberdosis/tiptap/issues/5602
- Official Docs: https://tiptap.dev/docs/editor/api/editor#immediatelyrender

### Prevention
- Add to editor configuration checklist
- Use base-editor.tsx template (includes fix)
- Test with `next build` before deploying

---

## Error #2: Headings/Lists Render Unstyled

### Symptoms
- Formatted content looks like plain text
- No visual difference between H1, H2, paragraph
- Lists show bullets but no indentation
- Links not colored/underlined

### Why It Happens
- Missing `@tailwindcss/typography` plugin
- No `prose` classes applied to container
- Custom CSS not loaded

### Solution A: Install Tailwind Typography (Recommended)

```bash
npm install @tailwindcss/typography
```

```typescript
// tailwind.config.ts
import typography from '@tailwindcss/typography'

export default {
  plugins: [typography],
}
```

```tsx
// Apply prose classes
<EditorContent
  editor={editor}
  className="prose prose-sm dark:prose-invert max-w-none"
/>
```

### Solution B: Custom CSS

Use `templates/tiptap-prose.css` from this skill:

```tsx
import './tiptap-prose.css'

<div className="tiptap">
  <EditorContent editor={editor} />
</div>
```

### References
- shadcn Discussion: https://github.com/shadcn-ui/ui/discussions/1729
- Tailwind Typography: https://github.com/tailwindlabs/tailwindcss-typography

---

## Error #3: Performance Issues / Editor Lags

### Symptoms
- Editor lags when typing
- Slow response to formatting commands
- High CPU usage during editing
- UI freezes on large documents

### Why It Happens
- `useEditor()` re-renders component on every change
- Large document tree causes expensive re-renders
- Extensions not memoized
- Too many extensions loaded

### Solution A: Use useEditorState for Read-Only

```typescript
import { useEditor, useEditorState } from '@tiptap/react'

function DisplayEditor({ content }: { content: string }) {
  const editor = useEditor({
    extensions: [StarterKit],
    content,
    editable: false,
    immediatelyRender: false,
  })

  // Only subscribe to specific state changes
  const { isFocused } = useEditorState({
    editor,
    selector: (ctx) => ({ isFocused: ctx.editor.isFocused }),
  })

  return <EditorContent editor={editor} />
}
```

### Solution B: Memoize Configuration

```typescript
import { useMemo } from 'react'

function Editor() {
  const extensions = useMemo(() => [
    StarterKit,
    Image,
    Link,
  ], [])

  const editor = useEditor({
    extensions,
    immediatelyRender: false,
  })

  return <EditorContent editor={editor} />
}
```

### Solution C: Lazy Load Extensions

Only load extensions when needed:

```typescript
const extensions = [
  StarterKit,
  // Only add Table if user needs tables
  ...(needsTables ? [Table, TableRow, TableCell] : []),
]
```

### References
- Performance Docs: https://tiptap.dev/docs/editor/getting-started/performance
- useEditorState: https://tiptap.dev/docs/editor/api/editor#useeditorstate

---

## Error #4: Image Upload Base64 Bloat

### Symptoms
- Database payload size in megabytes
- Slow saves/loads
- Database storage fills quickly
- JSON serialization takes long time

### Why It Happens
- Default Image extension allows base64
- Pasted images convert to base64 automatically
- No upload handler configured

### Solution
Set `allowBase64: false` and implement upload handler:

```typescript
import Image from '@tiptap/extension-image'

const editor = useEditor({
  extensions: [
    StarterKit,
    Image.configure({
      inline: true,
      allowBase64: false, // ⚠️ Prevent base64 bloat
    }),
  ],
  immediatelyRender: false,
})

// Implement upload handler
// See templates/image-upload-r2.tsx for full example
```

### Pattern
1. Insert base64 preview for immediate feedback
2. Upload to R2/S3 in background
3. Replace base64 with permanent URL
4. Store only URL in database

### References
- Image Extension Docs: https://tiptap.dev/docs/editor/extensions/nodes/image
- Upload Template: `templates/image-upload-r2.tsx`

---

## Error #5: Build Fails in Create React App

### Error Message
```
Module not found: Error: Can't resolve 'jsx-runtime'

or

Cannot find module '@tiptap/react'
```

### Why It Happens
- Tiptap v3 uses modern module structure
- Create React App (CRA) doesn't support it
- webpack configuration incompatibility

### Solution
Switch to Vite (recommended):

```bash
# Create new Vite project
npm create vite@latest my-project -- --template react-ts

# Install Tiptap
npm install @tiptap/react @tiptap/starter-kit @tiptap/pm

# Copy your components
```

### Alternative: Downgrade to Tiptap v2

```bash
npm install @tiptap/react@2.27.1 @tiptap/starter-kit@2.27.1
```

⚠️ Not recommended - v2 missing new features

### References
- GitHub Issue: https://github.com/ueberdosis/tiptap/issues/6812
- Vite Migration: https://vitejs.dev/guide/migration-from-cra.html

---

## Error #6: TypeScript Type Errors

### Error Message
```
Type 'Editor | null' is not assignable to type 'Editor'

or

Property 'chain' does not exist on type 'null'
```

### Why It Happens
- `useEditor()` returns `Editor | null`
- Editor is null during initial render
- TypeScript strict null checks

### Solution
Always check for null:

```typescript
const editor = useEditor({ ... })

if (!editor) {
  return null // or loading spinner
}

// Now safe to use editor
editor.chain().focus().toggleBold().run()
```

### Pattern for Event Handlers

```typescript
<button
  onClick={() => editor?.chain().focus().toggleBold().run()}
  disabled={!editor}
>
  Bold
</button>
```

---

## Error #7: Extensions Not Working

### Symptoms
- Extension installed but commands don't work
- Extension features not visible
- No error messages

### Why It Happens
- Extension not added to `extensions` array
- Extension loaded in wrong order
- Extension configuration incorrect

### Solution
```typescript
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image' // ← Must import

const editor = useEditor({
  extensions: [
    StarterKit,
    Image, // ← Must add to array
  ],
})
```

### Check Extension is Active

```typescript
if (editor.isActive('image')) {
  console.log('Image extension loaded')
}
```

### Extension Order Matters

Some extensions depend on others:

```typescript
const editor = useEditor({
  extensions: [
    // Base extensions first
    Document,
    Paragraph,
    Text,

    // Then marks/nodes that depend on them
    Bold,
    Image,
  ],
})
```

---

## Error #8: Content Not Updating

### Symptoms
- Editor content doesn't reflect prop changes
- `setContent` doesn't work
- Controlled component issues

### Why It Happens
- Editor content not synced with React state
- Missing `useEffect` to sync content
- Calling `setContent` during render

### Solution
Sync content in `useEffect`:

```typescript
import { useEffect } from 'react'

function Editor({ content }: { content: string }) {
  const editor = useEditor({
    extensions: [StarterKit],
    immediatelyRender: false,
  })

  // Sync external content changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  return <EditorContent editor={editor} />
}
```

---

## Error #9: Placeholder Not Showing

### Symptoms
- Placeholder text not visible
- Empty editor looks blank

### Why It Happens
- Placeholder extension not installed
- CSS for placeholder missing
- `editorProps` not configured

### Solution
```typescript
import Placeholder from '@tiptap/extension-placeholder'

const editor = useEditor({
  extensions: [
    StarterKit,
    Placeholder.configure({
      placeholder: 'Start writing...',
    }),
  ],
  editorProps: {
    attributes: {
      'data-placeholder': 'Start writing...',
    },
  },
})
```

CSS (in tiptap-prose.css):
```css
.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  color: var(--muted-foreground);
  float: left;
  height: 0;
  pointer-events: none;
}
```

---

## Error #10: Collaborative Editing Conflicts

### Symptoms
- Content overwrites between users
- Cursor positions wrong
- Undo/redo breaks

### Why It Happens
- Local history conflicts with Y.js
- Multiple users editing same node
- Network latency

### Solution
Disable local history for collaboration:

```typescript
import Collaboration from '@tiptap/extension-collaboration'

const editor = useEditor({
  extensions: [
    StarterKit.configure({
      history: false, // ⚠️ Disable for collaboration
    }),
    Collaboration.configure({
      document: ydoc,
    }),
  ],
})
```

---

## Debugging Tips

### Enable Tiptap Debug Mode

```typescript
const editor = useEditor({
  extensions: [StarterKit],
  enablePasteRules: true,
  enableInputRules: true,
  onBeforeCreate: ({ editor }) => {
    console.log('Editor creating:', editor)
  },
  onCreate: ({ editor }) => {
    console.log('Editor created:', editor)
  },
  onUpdate: ({ editor }) => {
    console.log('Editor updated:', editor.getJSON())
  },
})
```

### Inspect Editor State

```typescript
console.log(editor.getJSON()) // Current content as JSON
console.log(editor.getHTML()) // Current content as HTML
console.log(editor.state) // ProseMirror state
console.log(editor.extensionManager.extensions) // Loaded extensions
```

### Common Console Checks

```typescript
// Is extension loaded?
console.log(editor.extensionManager.extensions.map(e => e.name))

// Is editor editable?
console.log(editor.isEditable)

// What's selected?
console.log(editor.state.selection)

// Active marks/nodes?
console.log(editor.getAttributes('heading')) // { level: 2 }
```

---

**Last Verified**: 2025-11-29
**Tiptap Version**: 3.11.1
