import Editor from '@monaco-editor/react'

interface LatexEditorProps {
  value: string
  onChange: (value: string | undefined) => void
  height?: string
}

export default function LatexEditor({ value, onChange, height = '100%' }: LatexEditorProps) {
  return (
    <Editor
      height={height}
      defaultLanguage="latex"
      value={value}
      onChange={onChange}
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        automaticLayout: true,
      }}
    />
  )
}

