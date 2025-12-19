import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Image } from 'lucide-react'

interface FigureViewerProps {
  figures: Array<{ name: string; path: string }>
}

export default function FigureViewer({ figures }: FigureViewerProps) {
  if (figures.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Figures</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
            <Image className="h-12 w-12 mb-2" />
            <p>No figures available</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generated Figures</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {figures.map((figure, index) => (
            <div key={index} className="border rounded-lg overflow-hidden">
              <div className="aspect-video bg-muted flex items-center justify-center">
                <Image className="h-12 w-12 text-muted-foreground" />
              </div>
              <div className="p-2">
                <p className="text-sm font-medium truncate">{figure.name}</p>
                <a
                  href={figure.path}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary hover:underline"
                >
                  View
                </a>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

