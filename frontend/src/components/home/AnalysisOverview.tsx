import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import EmptyState from '@/components/layout/EmptyState'
import type {
  AnalysisCurves,
  AnalysisSummary,
  DashboardStats,
  HealthMonitorResponse,
} from '@/types/dashboard'

interface AnalysisOverviewProps {
  summary?: AnalysisSummary
  curves?: AnalysisCurves
  health?: HealthMonitorResponse
  stats?: DashboardStats
  isLoading: boolean
}

export default function AnalysisOverview({
  summary,
  curves,
  health,
  stats,
  isLoading,
}: AnalysisOverviewProps) {
  const chartData = curves
    ? curves.pi_curve.map((point, index) => ({
        x: point.x,
        pi: point.y,
        error: curves.error_curve[index]?.y ?? 0,
        bound: health?.riemann_bound[index]?.y ?? 0,
      }))
    : []

  return (
    <Card className="paper-panel">
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">
              Live Analysis
            </p>
            <CardTitle className="mt-2 text-3xl">ERH monitor</CardTitle>
          </div>
          <Badge variant={health?.violation ? 'destructive' : 'secondary'}>
            {health?.violation ? 'Bound violation' : 'Bound stable'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        {isLoading ? (
          <div className="h-[25rem] animate-pulse rounded-[1.4rem] bg-muted/70" />
        ) : !summary || chartData.length === 0 ? (
          <EmptyState
            title="No live analysis data yet"
            description="Seed the backend with mock ingestion or connect a real source to generate ERH curves and health signals."
          />
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                  Samples
                </p>
                <p className="mt-2 text-2xl font-semibold">{summary.num_samples}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                  Ethical primes
                </p>
                <p className="mt-2 text-2xl font-semibold">{summary.num_primes}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                  Estimated α
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  {summary.estimated_alpha?.toFixed(3) ?? 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                  Pass rate
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  {stats ? `${(stats.pass_rate * 100).toFixed(1)}%` : '0.0%'}
                </p>
              </div>
            </div>
            <div className="h-[22rem] rounded-[1.4rem] border border-border/70 bg-background/70 p-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(118, 126, 143, 0.24)" />
                  <XAxis dataKey="x" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="pi" stroke="hsl(var(--chart-2))" name="Π(x)" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="error" stroke="hsl(var(--chart-1))" name="E(x)" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="bound" stroke="hsl(var(--chart-3))" name="x^1/2 bound" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
