import { Link, useLocation } from 'react-router-dom'
import { FileEdit, Play, Settings, BookOpen, ScrollText } from 'lucide-react'
import { ROUTES } from '@/lib/constants'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Home', href: ROUTES.HOME, icon: BookOpen },
  { name: 'Editor', href: ROUTES.EDITOR, icon: FileEdit },
  { name: 'Simulation', href: ROUTES.SIMULATION, icon: Play },
  { name: 'Settings', href: ROUTES.SETTINGS, icon: Settings },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <div className="sticky top-0 hidden h-screen w-72 border-r border-border/60 bg-card/65 backdrop-blur xl:block">
      <div className="border-b border-border/70 p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-primary p-2 text-primary-foreground shadow-[0_12px_24px_rgba(32,48,71,0.28)]">
            <ScrollText className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Ethic-Latex</h1>
            <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">
              Research + Live Lab
            </p>
          </div>
        </div>
      </div>
      <div className="px-6 pt-6">
        <p className="text-sm leading-6 text-muted-foreground">
          Explore the ERH papers, generated figures, simulation runs, and formal rule verification from one interface.
        </p>
      </div>
      <nav className="space-y-2 p-4">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-2xl px-4 py-3 transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground shadow-[0_12px_32px_rgba(43,54,71,0.22)]'
                  : 'text-muted-foreground hover:bg-accent/70 hover:text-accent-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
