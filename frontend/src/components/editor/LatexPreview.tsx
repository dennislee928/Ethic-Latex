import 'katex/dist/katex.min.css'
import { BlockMath } from 'react-katex'

interface LatexPreviewProps {
  content: string
}

export default function LatexPreview({ content }: LatexPreviewProps) {
  if (!content || !content.trim()) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p>LaTeX preview will appear here</p>
      </div>
    )
  }

  // Try to render as block math, fallback to inline or text
  try {
    // For simplicity, just try to render the whole thing as block math
    // In production, you'd want more sophisticated parsing
    return (
      <div className="p-4 h-full overflow-auto">
        <div className="prose prose-sm max-w-none">
          <BlockMath math={content} />
        </div>
      </div>
    )
  } catch (error) {
    return (
      <div className="p-4 h-full overflow-auto">
        <div className="text-red-500">
          <p className="font-semibold">LaTeX Error:</p>
          <pre className="mt-2 text-xs">{String(error)}</pre>
        </div>
        <div className="mt-4 text-muted-foreground">
          <p>Raw content:</p>
          <pre className="mt-2 text-xs whitespace-pre-wrap">{content}</pre>
        </div>
      </div>
    )
  }
}

