import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Video, Music, Film, Clock, TrendingUp, Activity, Zap } from "lucide-react"

const stats = [
  { title: "Total Videos Generated", value: "1,234", change: "+12%", icon: Film, color: "text-blue-500" },
  { title: "Success Rate", value: "94.2%", change: "+2.1%", icon: TrendingUp, color: "text-green-500" },
  { title: "Active Video Pools", value: "156", change: "+8", icon: Video, color: "text-purple-500" },
  { title: "Active Music Pools", value: "42", change: "+3", icon: Music, color: "text-orange-500" },
]

const recentExecutions = [
  { id: "1", workflow: "Video Generation Pipeline", status: "success", startedAt: "2026-08-07 03:50", duration: "2m 34s" },
  { id: "2", workflow: "Music Download", status: "success", startedAt: "2026-08-07 03:46", duration: "1m 12s" },
  { id: "3", workflow: "Video Download", status: "success", startedAt: "2026-08-07 03:42", duration: "0m 45s" },
  { id: "4", workflow: "YouTube Upload", status: "success", startedAt: "2026-08-07 03:38", duration: "3m 21s" },
  { id: "5", workflow: "Video Generation Pipeline", status: "success", startedAt: "2026-08-07 03:30", duration: "2m 28s" },
]

const scheduledJobs = [
  { name: "Video Download", schedule: "Every 5 hours", nextRun: "In 2h 15m", status: "active" },
  { name: "Music Download", schedule: "Every 4 hours", nextRun: "In 1h 45m", status: "active" },
  { name: "Video Generation", schedule: "Daily at 18:00", nextRun: "In 14h 6m", status: "active" },
]

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.change} from last week</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Recent Executions
            </CardTitle>
            <CardDescription>Latest workflow runs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentExecutions.map((exec) => (
                <div key={exec.id} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{exec.workflow}</p>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {exec.startedAt} · {exec.duration}
                    </p>
                  </div>
                  <Badge variant={exec.status === "success" ? "default" : "destructive"}>
                    {exec.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Scheduled Jobs
            </CardTitle>
            <CardDescription>Automated workflow schedules</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {scheduledJobs.map((job, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{job.name}</p>
                    <p className="text-xs text-muted-foreground">{job.schedule}</p>
                  </div>
                  <div className="text-right">
                    <Badge variant="secondary">{job.status}</Badge>
                    <p className="text-xs text-muted-foreground mt-1">Next: {job.nextRun}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
          <CardDescription>n8n instance status</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>CPU Usage</span>
              <span>45%</span>
            </div>
            <Progress value={45} />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Memory Usage</span>
              <span>62%</span>
            </div>
            <Progress value={62} />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Disk Usage</span>
              <span>38%</span>
            </div>
            <Progress value={38} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
