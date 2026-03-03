# Tiptap Extension Catalog

**Last Updated**: 2025-11-29
**Last Verified**: 2025-11-29 (package versions, markdown API, Image resize option)

Comprehensive catalog of official and community Tiptap extensions.

---

## Official Extensions (Free)

### Included in StarterKit

**Marks** (formatting that can be applied to text):
- **Bold** - `@tiptap/extension-bold` - Bold text
- **Italic** - `@tiptap/extension-italic` - Italic text
- **Strike** - `@tiptap/extension-strike` - Strikethrough text
- **Code** - `@tiptap/extension-code` - Inline code formatting
- **Link** - `@tiptap/extension-link` - URL links (NEW in v3)
- **Underline** - `@tiptap/extension-underline` - Underline text (NEW in v3)

**Nodes** (content blocks):
- **Document** - `@tiptap/extension-document` - Root document
- **Paragraph** - `@tiptap/extension-paragraph` - Paragraph blocks
- **Text** - `@tiptap/extension-text` - Text content
- **Heading** - `@tiptap/extension-heading` - Headings (H1-H6)
- **BulletList** - `@tiptap/extension-bullet-list` - Unordered lists
- **OrderedList** - `@tiptap/extension-ordered-list` - Numbered lists
- **ListItem** - `@tiptap/extension-list-item` - List item nodes
- **Blockquote** - `@tiptap/extension-blockquote` - Quote blocks
- **CodeBlock** - `@tiptap/extension-code-block` - Code blocks
- **HorizontalRule** - `@tiptap/extension-horizontal-rule` - Horizontal dividers
- **HardBreak** - `@tiptap/extension-hard-break` - Line breaks

**Functionality**:
- **History** - `@tiptap/extension-history` - Undo/redo
- **Dropcursor** - `@tiptap/extension-dropcursor` - Drop cursor indicator
- **Gapcursor** - `@tiptap/extension-gapcursor` - Gap cursor for empty blocks
- **ListKeymap** - Keyboard shortcuts for lists (NEW in v3)
- **TrailingNode** - Ensures trailing paragraph (NEW in v3)

### Not in StarterKit (Install Separately)

**Media**:
- **Image** - `@tiptap/extension-image` - Images with src attribute
  ```typescript
  import Image from '@tiptap/extension-image'

  Image.configure({
    inline: true,
    allowBase64: false,
    resize: {
      enabled: true, // NEW: Drag-and-drop resizing
      directions: ['top-right', 'bottom-right', 'bottom-left', 'top-left'],
      minWidth: 100,
      minHeight: 100,
      alwaysPreserveAspectRatio: true,
    },
    HTMLAttributes: {
      class: 'rounded-lg',
    },
  })
  ```

**Text Styling**:
- **TextStyle** - `@tiptap/extension-text-style` - Text style container
- **Color** - `@tiptap/extension-color` - Text color
- **Highlight** - `@tiptap/extension-highlight` - Text highlighting
- **FontFamily** - `@tiptap/extension-font-family` - Font family control
- **Subscript** - `@tiptap/extension-subscript` - Subscript text
- **Superscript** - `@tiptap/extension-superscript` - Superscript text

**Content**:
- **Typography** - `@tiptap/extension-typography` - Smart quotes, dashes, ellipsis
  ```typescript
  import Typography from '@tiptap/extension-typography'

  // Converts:
  // (c) → ©
  // -> → →
  // ... → …
  // "text" → "text"
  ```

- **Placeholder** - `@tiptap/extension-placeholder` - Placeholder text
  ```typescript
  import Placeholder from '@tiptap/extension-placeholder'

  Placeholder.configure({
    placeholder: 'Start writing...',
    emptyEditorClass: 'is-editor-empty',
  })
  ```

**Tables**:
- **Table** - `@tiptap/extension-table` - Table container
- **TableRow** - `@tiptap/extension-table-row` - Table rows
- **TableCell** - `@tiptap/extension-table-cell` - Table cells
- **TableHeader** - `@tiptap/extension-table-header` - Table headers

```typescript
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'

const extensions = [
  Table.configure({
    resizable: true,
  }),
  TableRow,
  TableCell,
  TableHeader,
]
```

**Task Lists**:
- **TaskList** - `@tiptap/extension-task-list` - Task list container
- **TaskItem** - `@tiptap/extension-task-item` - Individual tasks

```typescript
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'

const extensions = [
  TaskList,
  TaskItem.configure({
    nested: true,
  }),
]
```

**Code Blocks**:
- **CodeBlockLowlight** - `@tiptap/extension-code-block-lowlight` - Syntax highlighted code
  ```typescript
  import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
  import { common, createLowlight } from 'lowlight'

  const lowlight = createLowlight(common)

  CodeBlockLowlight.configure({
    lowlight,
  })
  ```

**Collaboration**:
- **Collaboration** - `@tiptap/extension-collaboration` - Real-time collaboration
- **CollaborationCursor** - `@tiptap/extension-collaboration-cursor` - User cursors

```typescript
import Collaboration from '@tiptap/extension-collaboration'
import CollaborationCursor from '@tiptap/extension-collaboration-cursor'
import * as Y from 'yjs'

const ydoc = new Y.Doc()

const extensions = [
  Collaboration.configure({
    document: ydoc,
  }),
  CollaborationCursor.configure({
    provider,
    user: {
      name: 'John Doe',
      color: '#3b82f6',
    },
  }),
]
```

**Utilities**:
- **CharacterCount** - `@tiptap/extension-character-count` - Character/word count
- **Focus** - `@tiptap/extension-focus` - Focus management
- **TextAlign** - `@tiptap/extension-text-align` - Text alignment

---

## Official Pro Extensions (Paid)

Require Tiptap Pro subscription.

**AI-Powered**:
- **Content AI** - AI writing assistant
- **AI Image** - AI image generation

**Productivity**:
- **Comments** - Inline commenting
- **FileHandler** - Drag & drop file uploads
- **Mathematics** - Math equations (LaTeX)
- **TableOfContents** - Auto table of contents
- **UniqueID** - Unique IDs for nodes

**More**: https://tiptap.dev/pricing

---

## Community Extensions

Popular third-party extensions:

### Rich Media

**tiptap-extension-global-drag-handle**
- Drag handle for all blocks (Notion-like)
- GitHub: https://github.com/johanneskoch94/tiptap-extension-global-drag-handle

**@tiptap-pro/extension-emoji**
- Emoji picker integration
- GitHub: https://github.com/ueberdosis/tiptap-demos

**tiptap-youtube**
- YouTube video embeds
- npm: `tiptap-youtube`

**tiptap-audio**
- Audio player embeds
- npm: `tiptap-audio`

### Formatting

**tiptap-indent**
- Text indentation
- npm: `@joeattardi/tiptap-indent`

**tiptap-text-direction**
- RTL/LTR text direction
- npm: `tiptap-text-direction`

**tiptap-margin**
- Block margin control
- npm: `tiptap-margin`

### Interactive

**tiptap-mention**
- @mentions autocomplete
- GitHub: https://github.com/ueberdosis/tiptap/tree/main/packages/extension-mention

**tiptap-slash-command**
- Slash command menu (/)
- npm: `tiptap-slash-command`

**tiptap-extension-details-summary**
- Collapsible details/summary blocks
- npm: `tiptap-extension-details-summary`

### Markdown

**@tiptap/markdown** (Official, Recommended)
- Bidirectional markdown parser and serializer
- npm: `@tiptap/markdown@3.11.1`
- Import: `import { Markdown } from '@tiptap/markdown'`
- Released: October 15, 2025 (v3.7.0)
- Status: Beta (API stable but may evolve)
- Uses MarkedJS for CommonMark-compliant parsing
- Docs: https://tiptap.dev/docs/editor/markdown

```typescript
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import { Markdown } from '@tiptap/markdown'

const editor = new Editor({
  extensions: [StarterKit, Markdown],
  content: '# Hello World\n\nThis is **Markdown**!',
  contentType: 'markdown', // ⚠️ CRITICAL: Must specify
})

// Get markdown output
const markdown = editor.getMarkdown()

// Insert markdown
editor.commands.setContent('## New', { contentType: 'markdown' })
```

**tiptap-markdown** (Community, Legacy)
- Community markdown package (pre-official)
- npm: `tiptap-markdown@0.9.0`
- GitHub: https://github.com/aguingand/tiptap-markdown
- Status: Maintainer not planning v1, recommends official package
- Recommendation: Use official `@tiptap/markdown` instead

---

## Extension Development

### Creating Custom Extensions

**Node Extension Template**:
```typescript
import { Node } from '@tiptap/core'

export const CustomNode = Node.create({
  name: 'customNode',

  group: 'block',

  content: 'inline*',

  parseHTML() {
    return [
      {
        tag: 'div[data-custom]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', { 'data-custom': '', ...HTMLAttributes }, 0]
  },

  addCommands() {
    return {
      insertCustomNode: () => ({ commands }) => {
        return commands.insertContent({ type: this.name })
      },
    }
  },
})
```

**Mark Extension Template**:
```typescript
import { Mark } from '@tiptap/core'

export const CustomMark = Mark.create({
  name: 'customMark',

  parseHTML() {
    return [
      {
        tag: 'span[data-custom]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', { 'data-custom': '', ...HTMLAttributes }, 0]
  },

  addCommands() {
    return {
      toggleCustomMark: () => ({ commands }) => {
        return commands.toggleMark(this.name)
      },
    }
  },
})
```

**Extension Extension Template**:
```typescript
import { Extension } from '@tiptap/core'

export const CustomExtension = Extension.create({
  name: 'customExtension',

  addOptions() {
    return {
      // Custom options
    }
  },

  addCommands() {
    return {
      // Custom commands
    }
  },

  addKeyboardShortcuts() {
    return {
      'Mod-Shift-x': () => this.editor.commands.toggleCustomMark(),
    }
  },
})
```

### Resources

- **Custom Extensions Guide**: https://tiptap.dev/docs/editor/custom-extensions
- **Extension API**: https://tiptap.dev/docs/editor/api/extension
- **Examples**: https://github.com/ueberdosis/tiptap/tree/main/demos

---

## Extension Recommendations by Use Case

### Blog Editor
- StarterKit
- Image
- Link
- Typography
- Placeholder
- CharacterCount

### Comment System
- StarterKit (minimal config)
- Link
- Typography
- Placeholder
- CharacterCount (optional)

### Documentation
- StarterKit
- Image
- Table (+ TableRow, TableCell, TableHeader)
- CodeBlockLowlight
- TaskList (+ TaskItem)
- Typography
- TableOfContents (Pro)

### Notion-like Editor
- StarterKit
- Image
- Table
- TaskList
- CodeBlockLowlight
- Collaboration (+ CollaborationCursor)
- Slash commands (community)
- Drag handle (community)

### Form Input
- StarterKit (minimal)
- Placeholder
- CharacterCount
- TextAlign (optional)

---

## Installation Quick Reference

```bash
# Core
npm install @tiptap/react @tiptap/starter-kit @tiptap/pm

# Media
npm install @tiptap/extension-image

# Text Styling
npm install @tiptap/extension-text-style @tiptap/extension-color @tiptap/extension-highlight

# Content
npm install @tiptap/extension-typography @tiptap/extension-placeholder

# Tables
npm install @tiptap/extension-table @tiptap/extension-table-row @tiptap/extension-table-cell @tiptap/extension-table-header

# Task Lists
npm install @tiptap/extension-task-list @tiptap/extension-task-item

# Code Blocks with Syntax Highlighting
npm install @tiptap/extension-code-block-lowlight lowlight

# Collaboration
npm install @tiptap/extension-collaboration @tiptap/extension-collaboration-cursor yjs

# Utilities
npm install @tiptap/extension-character-count @tiptap/extension-focus @tiptap/extension-text-align
```

---

**Last Verified**: 2025-11-29
**Tiptap Version**: 3.11.1
