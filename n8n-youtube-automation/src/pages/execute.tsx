import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Loader2, CheckCircle2, XCircle, Clock, Zap } from "lucide-react"

interface ExecutionResult {
  id: string
  workflow: string
  status: "running" | "success" | "failed"
  startedAt: string
  duration?: string
  message?: string
}

const workflows = [
  { id: "video-pipeline", name: "Video Generation Pipeline", description: "Downloads videos, generates clips, and uploads to YouTube", triggers: ["Schedule Trigger2", "Manual"] },
  { id: "video-download", name: "Video Download", description: "Downloads video footage from YouTube", triggers: ["Schedule Trigger", "Manual"] },
  { id: "music-download", name: "Music Download", description: "Downloads music from YouTube", triggers: ["Schedule Trigger1", "Manual"] },
]

export default function Execute() {
  const [executions, setExecutions] = useState<ExecutionResult[]>([])
  const [runningWorkflow, setRunningWorkflow] = useState<string | null>(null)

  const executeWorkflow = async (workflowId: string) => {
    setRunningWorkflow(workflowId)
    const execId = Date.now().toString()
    const newExec: ExecutionResult = {
      id: execId,
      workflow: workflows.find(w => w.id === workflowId)?.name || workflowId,
      status: "running",
      startedAt: new Date().toLocaleString(),
    }
    setExecutions((prev) => [newExec, ...prev])

    setTimeout(() => {
      setExecutions((prev) =>
        prev.map((e) =>
          e.id === execId
            ? {
                ...e,
                status: "success" as const,
                duration: "2m 34s",
                message: "Workflow completed successfully",
              }
            : e
        )
      )
      setRunningWorkflow(null)
    }, 3000)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running": return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case "success": return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case "failed": return <XCircle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Execute Workflows</h2>
        <p className="text-muted-foreground">Manually trigger n8n workflows</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {workflows.map((workflow) => (
          <Card key={workflow.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-yellow-500" />
                {workflow.name}
              </CardTitle>
              <CardDescription>{workflow.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-1">
                {workflow.triggers.map((trigger) => (
                  <Badge key={trigger} variant="secondary" className="text-xs">
                    {trigger}
                  </Badge>
                ))}
              </div>
              <Button
                className="w-full"
                onClick={() => executeWorkflow(workflow.id)}
                disabled={runningWorkflow !== null}
              >
                {runningWorkflow === workflow.id ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Execute Now
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {executions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Execution History</CardTitle>
            <CardDescription>Recent manual executions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {executions.map((exec) => (
                <div key={exec.id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(exec.status)}
                    <div>
                      <p className="font-medium text-sm">{exec.workflow}</p>
                      <p className="text-xs text-muted-foreground">
                        Started: {exec.startedAt} {exec.duration && `· Duration: ${exec.duration}`}
                      </p>
                      {exec.message && <p className="text-xs text-muted-foreground mt-1">{exec.message}</p>}
                    </div>
                  </div>
                  <Badge variant={exec.status === "success" ? "default" : exec.status === "failed" ? "destructive" : "secondary"}>
                    {exec.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
