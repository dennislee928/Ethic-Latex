/**
 * Common Tiptap Extensions Bundle
 *
 * Pre-configured extensions for typical use cases:
 * - Blog editors
 * - Comment systems
 * - Documentation platforms
 * - Rich text inputs
 *
 * Installation:
 * npm install @tiptap/react @tiptap/starter-kit @tiptap/pm @tiptap/extension-image @tiptap/extension-link @tiptap/extension-typography @tiptap/extension-placeholder @tiptap/extension-text-style @tiptap/extension-color
 */

import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Typography from '@tiptap/extension-typography'
import Placeholder from '@tiptap/extension-placeholder'
import TextStyle from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import type { Extensions } from '@tiptap/react'

/**
 * Minimal Extension Set
 *
 * For simple text inputs (comments, descriptions, etc.)
 * Includes: Bold, Italic, Strike, Code, Hard Breaks
 */
export const minimalExtensions: Extensions = [
  StarterKit.configure({
    // Disable features not needed for simple inputs
    heading: false,
    bulletList: false,
    orderedList: false,
    blockquote: false,
    codeBlock: false,
    horizontalRule: false,
  }),
]

/**
 * Basic Extension Set
 *
 * For comment systems and basic rich text
 * Adds: Lists, Links, Typography
 */
export const basicExtensions: Extensions = [
  StarterKit.configure({
    heading: {
      levels: [2, 3], // Only H2, H3 for comments
    },
  }),
  Link.configure({
    openOnClick: false,
    HTMLAttributes: {
      class: 'text-primary underline underline-offset-2 hover:text-primary/80',
      rel: 'noopener noreferrer',
      target: '_blank',
    },
  }),
  Typography,
  Placeholder.configure({
    placeholder: 'Write a comment...',
  }),
]

/**
 * Standard Extension Set
 *
 * For blog posts, articles, documentation
 * Adds: Images, Color, All headings
 */
export const standardExtensions: Extensions = [
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
  Image.configure({
    inline: true,
    allowBase64: false, // Use upload handler instead
    HTMLAttributes: {
      class: 'rounded-lg max-w-full h-auto',
    },
  }),
  Link.configure({
    openOnClick: false,
    HTMLAttributes: {
      class: 'text-primary underline underline-offset-2 hover:text-primary/80',
      rel: 'noopener noreferrer',
      target: '_blank',
    },
  }),
  Typography,
  TextStyle,
  Color,
  Placeholder.configure({
    placeholder: 'Start writing...',
  }),
]

/**
 * Advanced Extension Set
 *
 * For full-featured editors (Notion-like)
 * Adds: Task lists, tables, code block lowlight, etc.
 *
 * Additional installs required:
 * npm install @tiptap/extension-task-list @tiptap/extension-task-item @tiptap/extension-table @tiptap/extension-table-row @tiptap/extension-table-cell @tiptap/extension-table-header @tiptap/extension-code-block-lowlight lowlight
 */
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { common, createLowlight } from 'lowlight'

const lowlight = createLowlight(common)

export const advancedExtensions: Extensions = [
  StarterKit.configure({
    heading: {
      levels: [1, 2, 3, 4, 5, 6],
    },
    codeBlock: false, // Replace with lowlight version
  }),
  CodeBlockLowlight.configure({
    lowlight,
    HTMLAttributes: {
      class: 'rounded-lg bg-muted p-4 font-mono text-sm overflow-x-auto',
    },
  }),
  Image.configure({
    inline: true,
    allowBase64: false,
    HTMLAttributes: {
      class: 'rounded-lg max-w-full h-auto',
    },
  }),
  Link.configure({
    openOnClick: false,
    HTMLAttributes: {
      class: 'text-primary underline underline-offset-2 hover:text-primary/80',
      rel: 'noopener noreferrer',
      target: '_blank',
    },
  }),
  TaskList.configure({
    HTMLAttributes: {
      class: 'list-none ml-0',
    },
  }),
  TaskItem.configure({
    nested: true,
    HTMLAttributes: {
      class: 'flex items-start gap-2',
    },
  }),
  Table.configure({
    resizable: true,
    HTMLAttributes: {
      class: 'border-collapse w-full my-4',
    },
  }),
  TableRow,
  TableHeader.configure({
    HTMLAttributes: {
      class: 'border border-border px-4 py-2 bg-muted font-semibold',
    },
  }),
  TableCell.configure({
    HTMLAttributes: {
      class: 'border border-border px-4 py-2',
    },
  }),
  Typography,
  TextStyle,
  Color,
  Placeholder.configure({
    placeholder: 'Start writing...',
  }),
]

/**
 * Collaborative Extension Set
 *
 * For real-time collaboration (Notion-like)
 *
 * Additional installs required:
 * npm install @tiptap/extension-collaboration @tiptap/extension-collaboration-cursor yjs y-websocket
 */
import Collaboration from '@tiptap/extension-collaboration'
import CollaborationCursor from '@tiptap/extension-collaboration-cursor'
import * as Y from 'yjs'

export function getCollaborativeExtensions(ydoc: Y.Doc, provider: any, user: { name: string; color: string }) {
  return [
    StarterKit.configure({
      history: false, // Disable local history for collaboration
    }),
    Collaboration.configure({
      document: ydoc,
    }),
    CollaborationCursor.configure({
      provider,
      user,
    }),
    Image.configure({
      inline: true,
      allowBase64: false,
    }),
    Link.configure({
      openOnClick: false,
    }),
    Typography,
  ]
}

/**
 * Usage Examples:
 *
 * // Minimal (comments)
 * const editor = useEditor({
 *   extensions: minimalExtensions,
 *   immediatelyRender: false,
 * })
 *
 * // Basic (rich comments)
 * const editor = useEditor({
 *   extensions: basicExtensions,
 *   immediatelyRender: false,
 * })
 *
 * // Standard (blog posts)
 * const editor = useEditor({
 *   extensions: standardExtensions,
 *   immediatelyRender: false,
 * })
 *
 * // Advanced (full editor)
 * const editor = useEditor({
 *   extensions: advancedExtensions,
 *   immediatelyRender: false,
 * })
 *
 * // Collaborative
 * const ydoc = new Y.Doc()
 * const provider = new WebsocketProvider('ws://localhost:1234', 'doc-name', ydoc)
 * const editor = useEditor({
 *   extensions: getCollaborativeExtensions(ydoc, provider, {
 *     name: 'John Doe',
 *     color: '#3b82f6',
 *   }),
 *   immediatelyRender: false,
 * })
 */

/**
 * Custom Extension Configuration Helpers
 */

/**
 * Get Link extension with custom validation
 */
export function getLinkExtensionWithValidation() {
  return Link.extend({
    addOptions() {
      return {
        ...this.parent?.(),
        validate: (href: string) => {
          // Only allow http(s) URLs
          return /^https?:\/\//.test(href)
        },
      }
    },
  })
}

/**
 * Get Image extension with size limits
 */
export function getImageExtensionWithLimits(maxWidth = 800, maxHeight = 600) {
  return Image.configure({
    inline: true,
    allowBase64: false,
    HTMLAttributes: {
      class: 'rounded-lg max-w-full h-auto',
      style: `max-width: ${maxWidth}px; max-height: ${maxHeight}px;`,
    },
  })
}

/**
 * Get Placeholder with dynamic text
 */
export function getPlaceholderExtension(text: string) {
  return Placeholder.configure({
    placeholder: text,
    emptyEditorClass: 'is-editor-empty',
    emptyNodeClass: 'is-empty',
    showOnlyWhenEditable: true,
    showOnlyCurrent: true,
  })
}
