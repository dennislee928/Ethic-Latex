import { Button } from '@/components/ui/button'
import { Play, Pause, SkipBack, SkipForward, RotateCcw } from 'lucide-react'

interface SimulationPlayerProps {
  isPlaying: boolean
  onPlay: () => void
  onPause: () => void
  onReset: () => void
  onStepBack: () => void
  onStepForward: () => void
  currentStep: number
  totalSteps: number
  disabled?: boolean
}

export default function SimulationPlayer({
  isPlaying,
  onPlay,
  onPause,
  onReset,
  onStepBack,
  onStepForward,
  currentStep,
  totalSteps,
  disabled = false,
}: SimulationPlayerProps) {
  return (
    <div className="flex items-center gap-2 p-4 bg-card border rounded-lg">
      <Button
        variant="outline"
        size="icon"
        onClick={onReset}
        disabled={disabled}
      >
        <RotateCcw className="h-4 w-4" />
      </Button>
      <Button
        variant="outline"
        size="icon"
        onClick={onStepBack}
        disabled={disabled || currentStep === 0}
      >
        <SkipBack className="h-4 w-4" />
      </Button>
      <Button
        variant="default"
        size="icon"
        onClick={isPlaying ? onPause : onPlay}
        disabled={disabled}
      >
        {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
      </Button>
      <Button
        variant="outline"
        size="icon"
        onClick={onStepForward}
        disabled={disabled || currentStep >= totalSteps - 1}
      >
        <SkipForward className="h-4 w-4" />
      </Button>
      <div className="flex-1 mx-4">
        <div className="flex items-center justify-between text-sm text-muted-foreground mb-1">
          <span>Step {currentStep + 1} of {totalSteps}</span>
          <span>{totalSteps > 0 ? Math.round(((currentStep + 1) / totalSteps) * 100) : 0}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all"
            style={{ width: `${totalSteps > 0 ? ((currentStep + 1) / totalSteps) * 100 : 0}%` }}
          />
        </div>
      </div>
    </div>
  )
}

