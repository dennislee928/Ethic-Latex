import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api/dashboard'
import type { JudgeType } from '@/types/dashboard'

interface RiskHeatmapProps {
  judgeType?: JudgeType
}

export default function RiskHeatmap({ judgeType = 'COMBINED' }: RiskHeatmapProps) {
  const { data: heatmapData, isLoading } = useQuery({
    queryKey: ['heatmap', judgeType],
    queryFn: () => dashboardApi.getHeatmap(judgeType),
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Heatmap</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-muted animate-pulse rounded" />
        </CardContent>
      </Card>
    )
  }

  if (!heatmapData || heatmapData.cells.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Heatmap</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No data available</p>
        </CardContent>
      </Card>
    )
  }

  // Find min and max delta for color scaling
  const deltas = heatmapData.cells.map((cell) => cell.delta_mean)
  const minDelta = Math.min(...deltas)
  const maxDelta = Math.max(...deltas)
  const range = maxDelta - minDelta || 1

  const getColor = (delta: number) => {
    const normalized = (delta - minDelta) / range
    if (normalized < 0.33) return 'bg-green-500'
    if (normalized < 0.66) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Heatmap (Complexity vs Delta)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="grid grid-cols-10 gap-1">
            {heatmapData.cells.map((cell, index) => (
              <div
                key={index}
                className={`${getColor(cell.delta_mean)} rounded p-2 text-white text-xs text-center`}
                style={{ opacity: Math.max(0.5, cell.count / Math.max(...heatmapData.cells.map((c) => c.count))) }}
                title={`Complexity: ${cell.complexity_bin.toFixed(2)}, Delta: ${cell.delta_mean.toFixed(2)}, Count: ${cell.count}`}
              >
                {cell.count}
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Low Risk</span>
            <span>High Risk</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

