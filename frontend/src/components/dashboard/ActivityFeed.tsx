import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Clock, Info, AlertTriangle, XCircle } from 'lucide-react'
import type { ActivityLog } from '@/types/dashboard'

interface ActivityFeedProps {
  activities?: ActivityLog[]
  isLoading?: boolean
}

export default function ActivityFeed({ activities, isLoading }: ActivityFeedProps) {
  // Mock data for demonstration
  const mockActivities: ActivityLog[] = activities || [
    {
      id: 1,
      timestamp: new Date().toISOString(),
      type: 'verification',
      message: 'Rule "Ethical Constraint A" verified successfully',
      severity: 'info',
    },
    {
      id: 2,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      type: 'violation',
      message: 'Critical violation detected in rule "Constraint B"',
      severity: 'error',
    },
    {
      id: 3,
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      type: 'simulation',
      message: 'Simulation #123 completed',
      severity: 'info',
    },
  ]

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />
      default:
        return <Info className="h-4 w-4 text-blue-600" />
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleDateString()
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Activity Feed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Feed</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {mockActivities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg border">
              <div className="mt-1">{getSeverityIcon(activity.severity)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="outline" className="text-xs">
                    {activity.type}
                  </Badge>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {formatTime(activity.timestamp)}
                  </div>
                </div>
                <p className="text-sm">{activity.message}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

