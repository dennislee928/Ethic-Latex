import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { simulateApi } from '@/api/simulate'
import { useDemoStore } from '@/store/demoStore'

export default function QuickSimulation() {
  const [numActions, setNumActions] = useState(1000)
  const [tau, setTau] = useState(0.3)
  const setSelectedSimulationId = useDemoStore((state) => state.setSelectedSimulationId)

  const simulationMutation = useMutation({
    mutationFn: () =>
      simulateApi.create({
        num_actions: numActions,
        tau,
        complexity_dist: 'zipf',
      }),
    onSuccess: (simulation) => {
      setSelectedSimulationId(simulation.id)
    },
  })

  return (
    <Card className="paper-panel">
      <CardHeader>
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">
          Quick Action
        </p>
        <CardTitle className="mt-2 text-3xl">Quick Simulation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">Actions</label>
            <Input
              type="number"
              min={100}
              max={10000}
              value={numActions}
              onChange={(event) => setNumActions(Number(event.target.value) || 1000)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Tau</label>
            <Input
              type="number"
              step="0.1"
              min={0}
              max={1}
              value={tau}
              onChange={(event) => setTau(Number(event.target.value) || 0.3)}
            />
          </div>
        </div>
        <Button onClick={() => simulationMutation.mutate()} disabled={simulationMutation.isPending}>
          {simulationMutation.isPending ? 'Launching…' : 'Launch simulation'}
        </Button>
        {simulationMutation.data ? (
          <Badge variant="secondary">Simulation #{simulationMutation.data.id} queued</Badge>
        ) : null}
      </CardContent>
    </Card>
  )
}
