import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import SimulationPlayer from '@/components/simulation/SimulationPlayer'
import TimelineGraph from '@/components/simulation/TimelineGraph'
import FigureViewer from '@/components/simulation/FigureViewer'
import { Play, Loader2 } from 'lucide-react'
import { simulateApi } from '@/api/simulate'
import type { SimulationCreate } from '@/types/simulation'

export default function Simulation() {
  const [simulationConfig, setSimulationConfig] = useState<SimulationCreate>({
    num_actions: 1000,
    complexity_dist: 'zipf',
    tau: 0.3,
  })
  const [selectedSimulationId, setSelectedSimulationId] = useState<number | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const queryClient = useQueryClient()

  // Fetch simulations list
  const { data: simulations } = useQuery({
    queryKey: ['simulations'],
    queryFn: () => simulateApi.list(),
  })

  // Fetch selected simulation
  const { data: simulation, isLoading: simulationLoading } = useQuery({
    queryKey: ['simulation', selectedSimulationId],
    queryFn: () => simulateApi.get(selectedSimulationId!),
    enabled: selectedSimulationId !== null,
  })

  // Fetch simulation results
  const { data: results } = useQuery({
    queryKey: ['simulation-results', selectedSimulationId],
    queryFn: () => simulateApi.getResults(selectedSimulationId!),
    enabled: selectedSimulationId !== null && simulation?.status === 'completed',
  })

  // Fetch simulation figures
  const { data: figures } = useQuery({
    queryKey: ['simulation-figures', selectedSimulationId],
    queryFn: () => simulateApi.getFigures(selectedSimulationId!),
    enabled: selectedSimulationId !== null,
  })

  // Create simulation mutation
  const createSimulation = useMutation({
    mutationFn: (config: SimulationCreate) => simulateApi.create(config),
    onSuccess: (data) => {
      setSelectedSimulationId(data.id)
      queryClient.invalidateQueries({ queryKey: ['simulations'] })
    },
  })

  const handleRunSimulation = () => {
    createSimulation.mutate(simulationConfig)
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'running':
        return 'secondary'
      case 'failed':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  // Prepare timeline data from results
  const timelineData = results
    ? Array.from({ length: 20 }, (_, i) => ({
        step: i,
        value: results.analysis.estimated_exponent + (Math.random() - 0.5) * 0.1,
      }))
    : undefined

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Simulation Visualizer</h1>
        <p className="text-muted-foreground mt-2">
          View psychohistory simulation results and visualizations
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left sidebar: Simulation list and config */}
        <div className="space-y-4">
          {/* Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Run Simulation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Number of Actions</label>
                <Input
                  type="number"
                  min={100}
                  max={10000}
                  value={simulationConfig.num_actions}
                  onChange={(e) =>
                    setSimulationConfig({
                      ...simulationConfig,
                      num_actions: parseInt(e.target.value) || 1000,
                    })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Complexity Distribution</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={simulationConfig.complexity_dist}
                  onChange={(e) =>
                    setSimulationConfig({
                      ...simulationConfig,
                      complexity_dist: e.target.value as 'zipf' | 'uniform' | 'power_law',
                    })
                  }
                >
                  <option value="zipf">Zipf</option>
                  <option value="uniform">Uniform</option>
                  <option value="power_law">Power Law</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Tau (Threshold)</label>
                <Input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={simulationConfig.tau}
                  onChange={(e) =>
                    setSimulationConfig({
                      ...simulationConfig,
                      tau: parseFloat(e.target.value) || 0.3,
                    })
                  }
                />
              </div>
              <Button
                onClick={handleRunSimulation}
                disabled={createSimulation.isPending}
                className="w-full"
              >
                {createSimulation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Run Simulation
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Simulation list */}
          <Card>
            <CardHeader>
              <CardTitle>Previous Simulations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {simulations?.map((sim) => (
                  <div
                    key={sim.id}
                    className={`p-3 rounded border cursor-pointer hover:bg-accent ${
                      selectedSimulationId === sim.id ? 'bg-accent' : ''
                    }`}
                    onClick={() => setSelectedSimulationId(sim.id)}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">Simulation #{sim.id}</span>
                      <Badge variant={getStatusBadgeVariant(sim.status)}>
                        {sim.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {new Date(sim.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main content: Results and visualizations */}
        <div className="lg:col-span-2 space-y-4">
          {selectedSimulationId && (
            <>
              {simulationLoading ? (
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-center">
                      <Loader2 className="h-8 w-8 animate-spin" />
                    </div>
                  </CardContent>
                </Card>
              ) : simulation?.status === 'completed' && results ? (
                <>
                  {/* Results summary */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Simulation Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Mistake Rate</p>
                          <p className="text-2xl font-bold">
                            {(results.mistake_rate * 100).toFixed(1)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Ethical Primes</p>
                          <p className="text-2xl font-bold">{results.ethical_primes_count}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Estimated Exponent</p>
                          <p className="text-2xl font-bold">
                            {results.analysis.estimated_exponent.toFixed(3)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">ERH Satisfied</p>
                          <Badge variant={results.analysis.erh_satisfied ? 'default' : 'destructive'}>
                            {results.analysis.erh_satisfied ? 'Yes' : 'No'}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Player controls */}
                  <SimulationPlayer
                    isPlaying={isPlaying}
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    onReset={() => setCurrentStep(0)}
                    onStepBack={() => setCurrentStep(Math.max(0, currentStep - 1))}
                    onStepForward={() => setCurrentStep(Math.min(19, currentStep + 1))}
                    currentStep={currentStep}
                    totalSteps={20}
                  />

                  {/* Timeline graph */}
                  <TimelineGraph data={timelineData} title="Simulation Timeline" />

                  {/* Figures */}
                  {figures && <FigureViewer figures={figures.figures} />}
                </>
              ) : (
                <Card>
                  <CardContent className="p-6">
                    <p className="text-muted-foreground">
                      Simulation status: {simulation?.status}. Results will appear here when completed.
                    </p>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {!selectedSimulationId && (
            <Card>
              <CardContent className="p-6">
                <p className="text-center text-muted-foreground">
                  Select a simulation from the list or run a new one to view results.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
