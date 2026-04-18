import JudgePicker from './JudgePicker'

export default function Header() {
  return (
    <header className="border-b border-border/70 bg-card/60 px-6 py-4 backdrop-blur">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-muted-foreground">
            Ethical Riemann Hypothesis
          </p>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">
            Hybrid research archive and live experiment interface
          </h2>
        </div>
        <div className="flex items-center gap-4">
          <JudgePicker />
        </div>
      </div>
    </header>
  )
}
