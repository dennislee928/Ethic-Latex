import { useQuery } from '@tanstack/react-query'
import SecurityMetrics from '@/components/dashboard/SecurityMetrics'
import RiskHeatmap from '@/components/dashboard/RiskHeatmap'
import LinterStats from '@/components/dashboard/LinterStats'
import ActivityFeed from '@/components/dashboard/ActivityFeed'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { dashboardApi } from '@/api/dashboard'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['analysis-summary'],
    queryFn: () => dashboardApi.getSummary('COMBINED'),
  })

  const { data: curves, isLoading: curvesLoading } = useQuery({
    queryKey: ['analysis-curves'],
    queryFn: () => dashboardApi.getCurves('COMBINED'),
  })

  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats(),
  })

  // Transform curves data for Recharts
  const chartData = curves
    ? curves.pi_curve.map((point: { x: number; y: number }, index: number) => ({
        x: point.x,
        pi: point.y,
        error: curves.error_curve[index]?.y || 0,
      }))
    : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Security & Ethics Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Overview of ethical rules and security analysis
        </p>
      </div>

      {/* Metrics Cards */}
      <SecurityMetrics stats={stats || null} isLoading={!stats} />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ERH Curves */}
        <Card>
          <CardHeader>
            <CardTitle>ERH Analysis Curves</CardTitle>
          </CardHeader>
          <CardContent>
            {curvesLoading ? (
              <div className="h-64 bg-muted animate-pulse rounded" />
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="x" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="pi" stroke="#8884d8" name="Π(x)" />
                  <Line type="monotone" dataKey="error" stroke="#82ca9d" name="E(x)" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

  {/* sdk */}
<a href="https://pypi.org/project/erh/0.1.0/" target="_blank">Python SDK</a>
<br />
<a href="https://www.npmjs.com/package/erh-js-sdk" target="_blank">node.js SDK</a>


        {/* Summary Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Analysis Summary</CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <div className="h-64 bg-muted animate-pulse rounded" />
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Judge Type:</span>
                  <span className="font-medium">{summary?.judge_type || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Samples:</span>
                  <span className="font-medium">{summary?.num_samples || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Primes:</span>
                  <span className="font-medium">{summary?.num_primes || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Estimated Alpha:</span>
                  <span className="font-medium">{summary?.estimated_alpha?.toFixed(3) || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">R²:</span>
                  <span className="font-medium">{summary?.r_squared?.toFixed(3) || 'N/A'}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Heatmap and Stats Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskHeatmap judgeType="COMBINED" />
        <LinterStats />
      </div>

      {/* Activity Feed */}
      <ActivityFeed />
    </div>
  )
}
