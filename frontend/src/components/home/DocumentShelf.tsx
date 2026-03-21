import { FileText } from 'lucide-react'
import EmptyState from '@/components/layout/EmptyState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { AssetRecord } from '@/types/assets'
import { cn } from '@/lib/utils'

interface DocumentShelfProps {
  documents: AssetRecord[]
  selectedUrl: string | null
  onSelect: (url: string) => void
}

export default function DocumentShelf({ documents, selectedUrl, onSelect }: DocumentShelfProps) {
  const selectedDocument = documents.find((document) => document.url === selectedUrl) ?? documents[0]

  return (
    <Card className="paper-panel">
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">
              Research Papers
            </p>
            <CardTitle className="mt-2 text-3xl">Root PDFs</CardTitle>
          </div>
          <Badge variant="secondary">{documents.length} indexed</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        {documents.length === 0 ? (
          <EmptyState
            title="No papers indexed yet"
            description="The backend asset route did not return any root PDFs. Add or restore the research papers in the repository root to surface them here."
          />
        ) : (
          <>
            <div className="grid gap-3 md:grid-cols-2">
              {documents.map((document) => (
                <Button
                  key={document.url}
                  variant={selectedDocument?.url === document.url ? 'default' : 'outline'}
                  className={cn(
                    'h-auto justify-start rounded-[1.25rem] px-4 py-4 text-left',
                    selectedDocument?.url !== document.url && 'bg-card/60'
                  )}
                  onClick={() => onSelect(document.url)}
                >
                  <div className="flex items-start gap-3">
                    <FileText className="mt-0.5 h-4 w-4" />
                    <div className="space-y-1">
                      <div className="font-semibold">{document.name}</div>
                      <div className="text-xs text-muted-foreground">{document.relativePath}</div>
                    </div>
                  </div>
                </Button>
              ))}
            </div>
            {selectedDocument ? (
              <div className="overflow-hidden rounded-[1.4rem] border border-border/70 bg-background/70">
                <div className="flex items-center justify-between border-b border-border/70 px-4 py-3">
                  <div>
                    <p className="font-semibold">{selectedDocument.name}</p>
                    <p className="text-xs text-muted-foreground">{selectedDocument.relativePath}</p>
                  </div>
                  <a
                    href={selectedDocument.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                  >
                    Open PDF
                  </a>
                </div>
                <iframe
                  title={selectedDocument.name}
                  src={selectedDocument.url}
                  className="h-[24rem] w-full bg-white"
                />
              </div>
            ) : null}
          </>
        )}
      </CardContent>
    </Card>
  )
}
