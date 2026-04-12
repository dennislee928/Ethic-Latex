import { Button } from '@/components/ui/button'
import { useDemoStore } from '@/store/demoStore'
import type { JudgeType } from '@/types/dashboard'
import { cn } from '@/lib/utils'

const judgeOptions: Array<{ label: string; value: JudgeType }> = [
  { label: 'Combined', value: 'COMBINED' },
  { label: 'Human', value: 'HUMAN' },
  { label: 'Pipeline', value: 'PIPELINE' },
]

export default function JudgePicker() {
  const judgeType = useDemoStore((state) => state.judgeType)
  const setJudgeType = useDemoStore((state) => state.setJudgeType)

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">
        Judge Lens
      </span>
      <div className="flex rounded-full border border-border/70 bg-card/80 p-1 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
        {judgeOptions.map((option) => (
          <Button
            key={option.value}
            type="button"
            size="sm"
            variant={judgeType === option.value ? 'default' : 'ghost'}
            className={cn(
              'rounded-full px-3',
              judgeType === option.value && 'shadow-[0_10px_20px_rgba(41,56,78,0.22)]'
            )}
            onClick={() => setJudgeType(option.value)}
          >
            {option.label}
          </Button>
        ))}
      </div>
    </div>
  )
}
