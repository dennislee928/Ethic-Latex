import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import LatexEditor from '@/components/editor/LatexEditor'
import LatexPreview from '@/components/editor/LatexPreview'
import ValidationPanel from '@/components/editor/ValidationPanel'
import SplitPane from '@/components/editor/SplitPane'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Save, Play } from 'lucide-react'
import { rulesApi } from '@/api/rules'
import { verifyApi } from '@/api/verify'
import type { LatexRule } from '@/types/latex'

export default function Editor() {
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null)
  const queryClient = useQueryClient()

  // Fetch rules
  const { data: rules } = useQuery({
    queryKey: ['rules'],
    queryFn: () => rulesApi.list(),
  })

  // Verify mutation
  const verifyMutation = useMutation({
    mutationFn: (latexContent: string) => verifyApi.verify(latexContent),
  })

  // Save rule mutation
  const saveMutation = useMutation({
    mutationFn: (rule: { title: string; content: string }) => {
      if (selectedRuleId) {
        return rulesApi.update(selectedRuleId, rule)
      }
      return rulesApi.create(rule)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
    },
  })

  const handleVerify = () => {
    if (content.trim()) {
      verifyMutation.mutate(content)
    }
  }

  const handleSave = () => {
    if (content.trim() && title.trim()) {
      saveMutation.mutate({ title, content })
    }
  }

  const handleLoadRule = (rule: LatexRule) => {
    setTitle(rule.title)
    setContent(rule.content)
    setSelectedRuleId(rule.id)
      verifyMutation.mutate(rule.content)
  }

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-3xl font-bold">LaTeX Alignment Editor</h1>
        <p className="text-muted-foreground mt-2">
          Write and verify ethical constraints in LaTeX
        </p>
      </div>

      <div className="flex gap-4 h-full">
        {/* Left sidebar with rules list */}
        <div className="w-64 border-r border-border">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Rules</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {rules?.map((rule) => (
                  <div
                    key={rule.id}
                    className="p-2 rounded border cursor-pointer hover:bg-accent"
                    onClick={() => handleLoadRule(rule)}
                  >
                    <p className="text-sm font-medium">{rule.title}</p>
                    <p className="text-xs text-muted-foreground truncate">{rule.content.substring(0, 50)}...</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main editor area */}
        <div className="flex-1 flex flex-col space-y-4">
          {/* Toolbar */}
          <div className="flex items-center gap-2">
            <Input
              placeholder="Rule title..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="max-w-xs"
            />
            <Button onClick={handleVerify} variant="outline">
              <Play className="h-4 w-4 mr-2" />
              Verify
            </Button>
            <Button onClick={handleSave} disabled={!content.trim() || !title.trim()}>
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
          </div>

          {/* Split pane: Editor | Preview */}
          <div className="flex-1 border border-border rounded-lg overflow-hidden">
            <SplitPane
              defaultSplit={50}
              left={
                <div className="h-full flex flex-col">
                  <div className="p-2 border-b border-border bg-muted/50">
                    <span className="text-sm font-medium">Editor</span>
                  </div>
                  <div className="flex-1">
                    <LatexEditor value={content} onChange={(value) => setContent(value || '')} />
                  </div>
                </div>
              }
              right={
                <div className="h-full flex flex-col">
                  <div className="p-2 border-b border-border bg-muted/50">
                    <span className="text-sm font-medium">Preview</span>
                  </div>
                  <div className="flex-1 bg-white">
                    <LatexPreview content={content} />
                  </div>
                </div>
              }
            />
          </div>

          {/* Validation panel */}
          <ValidationPanel
            validation={verifyMutation.data || null}
            isLoading={verifyMutation.isPending}
          />
        </div>
      </div>
    </div>
  )
}
