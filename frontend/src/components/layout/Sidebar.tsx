import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, FileEdit, Play, Settings, BookOpen } from 'lucide-react'
import { ROUTES } from '@/lib/constants'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { name: 'Editor', href: ROUTES.EDITOR, icon: FileEdit },
  { name: 'Simulation', href: ROUTES.SIMULATION, icon: Play },
  { name: 'Settings', href: ROUTES.SETTINGS, icon: Settings },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <div className="w-64 bg-card border-r border-border h-screen sticky top-0">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold">Ethic-Latex</h1>
        </div>
      </div>
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-2 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
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

