import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

interface LinterStatsProps {
  data?: Array<{ name: string; count: number; severity: string }>
}

export default function LinterStats({ data }: LinterStatsProps) {
  // Mock data for demonstration
  const chartData = data || [
    { name: 'Security Bypass', count: 12, severity: 'critical' },
    { name: 'Unbalanced Braces', count: 8, severity: 'medium' },
    { name: 'Invalid Syntax', count: 5, severity: 'low' },
    { name: 'Missing Conditions', count: 3, severity: 'low' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Linter Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#8884d8" name="Violations" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

