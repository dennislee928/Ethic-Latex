import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { useEffect } from 'react'

interface EditorProps {
  content?: string
  onUpdate?: (content: string) => void
  placeholder?: string
  editable?: boolean
  className?: string
}

/**
 * Base Tiptap Editor Component
 *
 * Features:
 * - SSR-safe (immediatelyRender: false)
 * - Tailwind Typography prose classes
 * - StarterKit with all basic extensions
 * - Update callback for form integration
 * - Customizable placeholder
 * - Editable/readonly modes
 *
 * Usage:
 * ```tsx
 * import { Editor } from '@/components/editor'
 *
 * function MyComponent() {
 *   const [content, setContent] = useState('')
 *
 *   return (
 *     <Editor
 *       content={content}
 *       onUpdate={setContent}
 *       placeholder="Start writing..."
 *     />
 *   )
 * }
 * ```
 */
export function Editor({
  content = '',
  onUpdate,
  placeholder = 'Start writing...',
  editable = true,
  className = '',
}: EditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4],
        },
        bulletList: {
          keepMarks: true,
          keepAttributes: false,
        },
        orderedList: {
          keepMarks: true,
          keepAttributes: false,
        },
      }),
    ],
    content,
    editable,
    immediatelyRender: false, // ⚠️ CRITICAL: Prevents SSR hydration errors
    editorProps: {
      attributes: {
        class: `prose prose-sm sm:prose-base lg:prose-lg dark:prose-invert max-w-none focus:outline-none min-h-[200px] p-4 ${className}`,
        'data-placeholder': placeholder,
      },
    },
    onUpdate: ({ editor }) => {
      onUpdate?.(editor.getHTML())
    },
  })

  // Sync content changes from parent
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  if (!editor) {
    return null
  }

  return (
    <div className="border border-border rounded-lg bg-background">
      <EditorContent editor={editor} />
    </div>
  )
}

/**
 * Editor with Toolbar
 *
 * Includes basic formatting toolbar above editor content.
 * For more advanced toolbars, use shadcn minimal-tiptap component.
 */
export function EditorWithToolbar(props: EditorProps) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: props.content,
    immediatelyRender: false,
    onUpdate: ({ editor }) => {
      props.onUpdate?.(editor.getHTML())
    },
  })

  if (!editor) {
    return null
  }

  return (
    <div className="border border-border rounded-lg bg-background">
      {/* Basic Toolbar */}
      <div className="flex flex-wrap gap-1 p-2 border-b border-border">
        <button
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={`px-3 py-1 rounded hover:bg-accent ${
            editor.isActive('bold') ? 'bg-accent' : ''
          }`}
          type="button"
        >
          Bold
        </button>
        <button
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={`px-3 py-1 rounded hover:bg-accent ${
            editor.isActive('italic') ? 'bg-accent' : ''
          }`}
          type="button"
        >
          Italic
        </button>
        <button
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={`px-3 py-1 rounded hover:bg-accent ${
            editor.isActive('heading', { level: 2 }) ? 'bg-accent' : ''
          }`}
          type="button"
        >
          H2
        </button>
        <button
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={`px-3 py-1 rounded hover:bg-accent ${
            editor.isActive('bulletList') ? 'bg-accent' : ''
          }`}
          type="button"
        >
          List
        </button>
      </div>

      {/* Editor Content */}
      <EditorContent editor={editor} className="p-4" />
    </div>
  )
}
