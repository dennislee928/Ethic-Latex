import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface TimelineGraphProps {
  data?: Array<{ step: number; value: number; label?: string }>
  title?: string
}

export default function TimelineGraph({ data, title = 'Timeline' }: TimelineGraphProps) {
  // Mock data for demonstration
  const chartData = data || Array.from({ length: 20 }, (_, i) => ({
    step: i,
    value: Math.sin(i / 2) * 10 + 50 + Math.random() * 10,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="step" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#8884d8" name="Value" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

