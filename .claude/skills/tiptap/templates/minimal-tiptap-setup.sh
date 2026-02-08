#!/bin/bash
#
# shadcn Minimal Tiptap Component Installation
#
# This script installs the official shadcn minimal-tiptap component
# which provides a fully-featured editor with:
# - Comprehensive toolbar
# - Image upload support
# - Code block with syntax highlighting
# - Link handling
# - Typography extension
# - Dark mode support
#
# Usage:
#   chmod +x minimal-tiptap-setup.sh
#   ./minimal-tiptap-setup.sh
#

set -e

echo "📦 Installing shadcn minimal-tiptap component..."

# Install the component via shadcn CLI
npx shadcn@latest add https://raw.githubusercontent.com/Aslam97/shadcn-minimal-tiptap/main/registry/block-registry.json

echo "📦 Installing required dependencies..."

# Install Tiptap core packages
npm install @tiptap/react @tiptap/starter-kit @tiptap/pm

# Install additional extensions used by minimal-tiptap
npm install @tiptap/extension-image \
  @tiptap/extension-color \
  @tiptap/extension-text-style \
  @tiptap/extension-typography \
  @tiptap/extension-code-block-lowlight \
  lowlight \
  react-medium-image-zoom

echo "✅ Installation complete!"
echo ""
echo "📚 Usage Example:"
echo ""
echo "import { MinimalTiptapEditor } from '@/components/minimal-tiptap'"
echo ""
echo "function MyComponent() {"
echo "  const [content, setContent] = useState('')"
echo "  "
echo "  return ("
echo "    <MinimalTiptapEditor"
echo "      value={content}"
echo "      onChange={setContent}"
echo "      placeholder='Start writing...'"
echo "    />"
echo "  )"
echo "}"
echo ""
echo "📖 Documentation: https://github.com/Aslam97/shadcn-minimal-tiptap"
