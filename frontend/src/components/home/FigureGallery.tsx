import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import EmptyState from '@/components/layout/EmptyState'
import type { AssetRecord } from '@/types/assets'

interface FigureGalleryProps {
  figures: AssetRecord[]
  selectedUrl: string | null
  onSelect: (url: string) => void
}

export default function FigureGallery({ figures, selectedUrl, onSelect }: FigureGalleryProps) {
  const selectedFigure = figures.find((figure) => figure.url === selectedUrl) ?? figures[0]

  return (
    <Card className="paper-panel">
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">
              Visual Archive
            </p>
            <CardTitle className="mt-2 text-3xl">Figure Gallery</CardTitle>
          </div>
          <Badge variant="secondary">{figures.length} indexed</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        {figures.length === 0 ? (
          <EmptyState
            title="No figures indexed yet"
            description="The generated figure directories are currently empty. Run the simulation or add figure outputs to populate this gallery."
          />
        ) : (
          <>
            <div className="flex flex-wrap gap-2">
              {figures.slice(0, 12).map((figure) => (
                <Button
                  key={figure.url}
                  variant={selectedFigure?.url === figure.url ? 'default' : 'outline'}
                  size="sm"
                  className="rounded-full"
                  onClick={() => onSelect(figure.url)}
                >
                  {figure.name}
                </Button>
              ))}
            </div>
            {selectedFigure ? (
              <div className="overflow-hidden rounded-[1.4rem] border border-border/70 bg-background/70">
                <div className="flex items-center justify-between border-b border-border/70 px-4 py-3">
                  <div>
                    <p className="font-semibold">{selectedFigure.name}</p>
                    <p className="text-xs text-muted-foreground">{selectedFigure.category}</p>
                  </div>
                  <a
                    href={selectedFigure.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                  >
                    Open figure
                  </a>
                </div>
                <iframe
                  title={selectedFigure.name}
                  src={selectedFigure.url}
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
