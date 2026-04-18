import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import PageIntro from '@/components/layout/PageIntro'
import type { AnalysisSummary, DashboardStats } from '@/types/dashboard'

interface HeroPanelProps {
  summary?: AnalysisSummary
  stats?: DashboardStats
  documentCount: number
  figureCount: number
  onRunMockIngestion: () => void
  isRunningMockIngestion: boolean
}

function StatBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="paper-panel p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">
        {label}
      </p>
      <p className="mt-3 text-3xl font-semibold text-foreground">{value}</p>
    </div>
  )
}

export default function HeroPanel({
  summary,
  stats,
  documentCount,
  figureCount,
  onRunMockIngestion,
  isRunningMockIngestion,
}: HeroPanelProps) {
  return (
    <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
      <div className="paper-panel overflow-hidden p-8">
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="secondary">Root PDFs integrated</Badge>
          <Badge variant="outline">FastAPI live data</Badge>
          <Badge variant="outline">Simulation + verification</Badge>
        </div>
        <div className="mt-6">
          <PageIntro
            eyebrow="Hybrid Demo"
            title="A research archive and live laboratory for the Ethical Riemann Hypothesis."
            description="This interface reads the project’s papers and generated figures as first-class assets while exposing the backend’s analysis, simulation, and verification workflows in the same surface."
          />
        </div>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button onClick={onRunMockIngestion} disabled={isRunningMockIngestion}>
            {isRunningMockIngestion ? 'Running mock ingestion…' : 'Run Mock Ingestion'}
          </Button>
          <div className="rounded-full border border-border/70 px-4 py-2 text-sm text-muted-foreground">
            Active judge: {summary?.judge_type ?? 'COMBINED'}
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
        <StatBlock label="Paper Index" value={String(documentCount)} />
        <StatBlock label="Generated Figures" value={String(figureCount)} />
        <StatBlock label="Samples" value={String(summary?.num_samples ?? 0)} />
        <StatBlock
          label="Pass Rate"
          value={stats ? `${(stats.pass_rate * 100).toFixed(1)}%` : '0.0%'}
        />
      </div>
    </section>
  )
}
