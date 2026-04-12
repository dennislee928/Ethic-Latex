import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { verifyApi } from '@/api/verify'

const DEFAULT_LATEX = String.raw`\forall a \in A,\ |E(a)| \leq C \cdot x^{1/2 + \epsilon}`

export default function QuickVerifier() {
  const [content, setContent] = useState(DEFAULT_LATEX)

  const verificationMutation = useMutation({
    mutationFn: () => verifyApi.verify(content),
  })

  return (
    <Card className="paper-panel">
      <CardHeader>
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">
          Quick Action
        </p>
        <CardTitle className="mt-2 text-3xl">Quick Verifier</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          className="min-h-[10rem] rounded-[1.2rem] bg-background/70"
        />
        <Button onClick={() => verificationMutation.mutate()} disabled={verificationMutation.isPending}>
          {verificationMutation.isPending ? 'Verifying…' : 'Verify LaTeX rule'}
        </Button>
        {verificationMutation.data ? (
          <div className="flex flex-wrap gap-2">
            <Badge variant={verificationMutation.data.is_valid ? 'secondary' : 'destructive'}>
              {verificationMutation.data.is_valid ? 'Valid' : 'Review needed'}
            </Badge>
            <Badge variant="outline">
              Risk {verificationMutation.data.risk_score.toFixed(2)}
            </Badge>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
