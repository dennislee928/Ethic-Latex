import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Shield, AlertTriangle, CheckCircle, FileText } from 'lucide-react'
import type { DashboardStats } from '@/types/dashboard'

interface SecurityMetricsProps {
  stats: DashboardStats | null
  isLoading?: boolean
}

export default function SecurityMetrics({ stats, isLoading }: SecurityMetricsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <div className="h-4 bg-muted animate-pulse rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const metrics = [
    {
      title: 'Total Rules',
      value: stats?.total_rules || 0,
      icon: FileText,
      color: 'text-blue-600',
    },
    {
      title: 'Active Rules',
      value: stats?.active_rules || 0,
      icon: CheckCircle,
      color: 'text-green-600',
    },
    {
      title: 'Pass Rate',
      value: `${((stats?.pass_rate || 0) * 100).toFixed(1)}%`,
      icon: Shield,
      color: 'text-blue-600',
    },
    {
      title: 'Total Violations',
      value: stats?.total_violations || 0,
      icon: AlertTriangle,
      color: 'text-orange-600',
    },
    {
      title: 'Critical Violations',
      value: stats?.critical_violations || 0,
      icon: AlertTriangle,
      color: 'text-red-600',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {metrics.map((metric) => {
        const Icon = metric.icon
        return (
          <Card key={metric.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
              <Icon className={`h-4 w-4 ${metric.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

