import {
  LayoutDashboard,
  Video,
  Music,
  Film,
  Play,
  Settings,
  PlayCircle,
  Menu,
  X,
  Activity,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Video, label: "Video Pools", href: "/video-pools" },
  { icon: Music, label: "Music Pools", href: "/music-pools" },
  { icon: Film, label: "Video Logs", href: "/video-logs" },
  { icon: Play, label: "Execute", href: "/execute" },
  { icon: Settings, label: "Settings", href: "/settings" },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
  currentPath: string
}

export function Sidebar({ collapsed, onToggle, currentPath }: SidebarProps) {
  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen border-r bg-background transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 border-b">
        {!collapsed && (
          <div className="flex items-center gap-2 font-bold text-lg">
            <PlayCircle className="h-6 w-6 text-red-500" />
            <span>YT Automate</span>
          </div>
        )}
        <Button variant="ghost" size="icon" onClick={onToggle} className="shrink-0">
          {collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
        </Button>
      </div>
      <nav className="flex flex-col gap-1 p-2">
        {navItems.map((item) => {
          const isActive = currentPath === item.href || (item.href !== "/" && currentPath.startsWith(item.href))
          return (
            <a
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </a>
          )
        })}
      </nav>
      {!collapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Activity className="h-3 w-3 text-green-500" />
            <span>n8n Connected</span>
          </div>
        </div>
      )}
    </aside>
  )
}
