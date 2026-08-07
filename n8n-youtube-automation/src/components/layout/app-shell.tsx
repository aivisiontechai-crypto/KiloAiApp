import { useState } from "react"
import { Outlet, useLocation } from "react-router-dom"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"

const pageConfig: Record<string, { title: string; subtitle?: string }> = {
  "/": { title: "Dashboard", subtitle: "Overview of your YouTube automation pipeline" },
  "/video-pools": { title: "Video Pools", subtitle: "Manage your source video assets" },
  "/music-pools": { title: "Music Pools", subtitle: "Manage your background music assets" },
  "/video-logs": { title: "Video Logs", subtitle: "History of generated and uploaded videos" },
  "/execute": { title: "Execute", subtitle: "Manually trigger workflows" },
  "/settings": { title: "Settings", subtitle: "Configure n8n integration" },
}

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const config = pageConfig[location.pathname] || { title: "YouTube Automation" }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} currentPath={location.pathname} />
      <div className={cn("transition-all duration-300", collapsed ? "ml-16" : "ml-64")}>
        <Header title={config.title} subtitle={config.subtitle} />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ")
}
