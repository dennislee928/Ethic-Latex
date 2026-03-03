# Tiptap Documentation Quick Reference

**Last Updated**: 2025-11-29

This reference provides quick links to essential Tiptap documentation for common tasks.

---

## Official Documentation

### Core Docs
- **Main Site**: https://tiptap.dev
- **Installation (React)**: https://tiptap.dev/docs/editor/installation/react
- **Getting Started**: https://tiptap.dev/docs/editor/getting-started/overview
- **API Reference**: https://tiptap.dev/docs/editor/api/editor

### Key Concepts
- **Extensions**: https://tiptap.dev/docs/editor/extensions
- **Commands**: https://tiptap.dev/docs/editor/api/commands
- **Nodes**: https://tiptap.dev/docs/editor/core-concepts/schema#nodes
- **Marks**: https://tiptap.dev/docs/editor/core-concepts/schema#marks
- **Collaborative Editing**: https://tiptap.dev/docs/editor/getting-started/collaborative-editing

---

## React Integration

### useEditor Hook
- **API Docs**: https://tiptap.dev/docs/editor/api/editor
- **Configuration Options**: https://tiptap.dev/docs/editor/api/editor#editor-configuration
- **immediatelyRender**: https://tiptap.dev/docs/editor/api/editor#immediatelyrender

### Performance
- **React Performance Guide**: https://tiptap.dev/docs/editor/getting-started/performance
- **useEditorState Hook**: https://tiptap.dev/docs/editor/api/editor#useeditorstate

---

## Extensions Documentation

### StarterKit
- **Overview**: https://tiptap.dev/docs/editor/extensions/functionality/starterkit
- **Included Extensions**:
  - Bold: https://tiptap.dev/docs/editor/extensions/marks/bold
  - Italic: https://tiptap.dev/docs/editor/extensions/marks/italic
  - Strike: https://tiptap.dev/docs/editor/extensions/marks/strike
  - Code: https://tiptap.dev/docs/editor/extensions/marks/code
  - Heading: https://tiptap.dev/docs/editor/extensions/nodes/heading
  - Paragraph: https://tiptap.dev/docs/editor/extensions/nodes/paragraph
  - BulletList: https://tiptap.dev/docs/editor/extensions/nodes/bullet-list
  - OrderedList: https://tiptap.dev/docs/editor/extensions/nodes/ordered-list
  - Blockquote: https://tiptap.dev/docs/editor/extensions/nodes/blockquote
  - CodeBlock: https://tiptap.dev/docs/editor/extensions/nodes/code-block
  - HorizontalRule: https://tiptap.dev/docs/editor/extensions/nodes/horizontal-rule
  - Link: https://tiptap.dev/docs/editor/extensions/marks/link (NEW in v3)
  - Underline: https://tiptap.dev/docs/editor/extensions/marks/underline (NEW in v3)

### Popular Extensions
- **Image**: https://tiptap.dev/docs/editor/extensions/nodes/image
- **Link**: https://tiptap.dev/docs/editor/extensions/marks/link
- **Typography**: https://tiptap.dev/docs/editor/extensions/marks/typography
- **Placeholder**: https://tiptap.dev/docs/editor/extensions/functionality/placeholder
- **Color**: https://tiptap.dev/docs/editor/extensions/marks/color
- **TaskList**: https://tiptap.dev/docs/editor/extensions/nodes/task-list
- **Table**: https://tiptap.dev/docs/editor/extensions/nodes/table
- **CodeBlockLowlight**: https://tiptap.dev/docs/editor/extensions/nodes/code-block-lowlight

### Collaboration Extensions
- **Collaboration**: https://tiptap.dev/docs/editor/extensions/functionality/collaboration
- **CollaborationCursor**: https://tiptap.dev/docs/editor/extensions/functionality/collaboration-cursor

---

## Tailwind Integration

### shadcn minimal-tiptap
- **GitHub**: https://github.com/Aslam97/shadcn-minimal-tiptap
- **Live Demo**: https://shadcn-minimal-tiptap.vercel.app
- **Installation**: https://github.com/Aslam97/shadcn-minimal-tiptap#installation

### Tailwind Typography
- **Plugin Docs**: https://github.com/tailwindlabs/tailwindcss-typography
- **Configuration**: https://github.com/tailwindlabs/tailwindcss-typography#configuration
- **Customization**: https://github.com/tailwindlabs/tailwindcss-typography#customization

---

## Common Tasks

### Creating Custom Extensions
- **Guide**: https://tiptap.dev/docs/editor/custom-extensions
- **Extension API**: https://tiptap.dev/docs/editor/api/extension
- **Node Extensions**: https://tiptap.dev/docs/editor/custom-extensions/create-a-node
- **Mark Extensions**: https://tiptap.dev/docs/editor/custom-extensions/create-a-mark

### Working with Content
- **Get Content**: https://tiptap.dev/docs/editor/api/editor#get-content
- **Set Content**: https://tiptap.dev/docs/editor/api/editor#set-content
- **JSON**: https://tiptap.dev/docs/editor/core-concepts/schema#json
- **HTML**: https://tiptap.dev/docs/editor/api/utilities/html

### Styling
- **Editor Props**: https://tiptap.dev/docs/editor/api/editor#editor-props
- **CSS Classes**: https://tiptap.dev/docs/editor/getting-started/style-editor

---

## Migration Guides

### Upgrading to v3
- **Migration Guide**: https://tiptap.dev/docs/editor/migration/v2-to-v3
- **Breaking Changes**: Key changes include:
  - `immediatelyRender` now required for SSR
  - Link extension moved to StarterKit
  - Underline extension moved to StarterKit
  - New list handling (ListKeymap)

### From Other Editors
- **From Slate**: Community comparison available
- **From ProseMirror**: Tiptap is built on ProseMirror
- **From Lexical**: Different architecture (consider use cases)

---

## Examples & Tutorials

### Official Examples
- **Examples Repository**: https://github.com/ueberdosis/tiptap/tree/main/demos
- **CodeSandbox**: https://codesandbox.io/examples/package/@tiptap/react
- **Live Playground**: https://tiptap.dev/examples

### Community Resources
- **shadcn-ui Discussions**: https://github.com/shadcn-ui/ui/discussions?discussions_q=tiptap
- **Stack Overflow Tag**: https://stackoverflow.com/questions/tagged/tiptap
- **Discord Community**: https://discord.gg/WtJ49jGshW

---

## GitHub

- **Main Repository**: https://github.com/ueberdosis/tiptap
- **Issues**: https://github.com/ueberdosis/tiptap/issues
- **Releases**: https://github.com/ueberdosis/tiptap/releases
- **Changelog**: https://github.com/ueberdosis/tiptap/blob/main/CHANGELOG.md

---

## Context7 MCP

When using Context7 MCP for Tiptap documentation:

**Library ID**: `tiptap/tiptap`

**Example Query**:
```
resolve-library-id --library-name "tiptap"
```

**Common Queries**:
- "How to configure immediatelyRender for SSR"
- "Image extension configuration options"
- "Collaborative editing setup with Y.js"
- "Custom extension creation guide"

---

## Pro Extensions (Paid)

For reference - require Tiptap Pro subscription:
- **Content AI**: https://tiptap.dev/docs/content-ai
- **Comments**: https://tiptap.dev/docs/comments
- **FileHandler**: https://tiptap.dev/docs/file-handler
- **Mathematics**: https://tiptap.dev/docs/mathematics
- **TableOfContents**: https://tiptap.dev/docs/table-of-contents

---

## Quick Links by Use Case

### Blog/Article Editor
1. StarterKit configuration
2. Image extension with upload
3. Link extension
4. Typography extension
5. Tailwind prose styling

### Comment System
1. Minimal StarterKit (no headings)
2. Link extension
3. Placeholder
4. Compact prose styling

### Documentation Platform
1. Full StarterKit
2. Table extension
3. CodeBlockLowlight
4. TaskList
5. Typography

### Collaborative Editor
1. Collaboration extension
2. CollaborationCursor
3. Y.js integration
4. WebSocket provider

---

**Last Verified**: 2025-11-29
**Tiptap Version**: 3.11.1
