import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Search, ExternalLink, Eye } from "lucide-react"

interface VideoLog {
  id: string
  videoTitle: string
  videoTranscript: string
  status: string
  youtubeLink?: string
  outputPath?: string
  postTime?: string
  rowNumber: string
}

const mockLogs: VideoLog[] = [
  { id: "1", videoTitle: "Motivational Quote #1", videoTranscript: "The only way to do great work is to love what you do.", status: "Success", youtubeLink: "https://youtube.com/watch?v=abc123", outputPath: "./vid_abc123.mp4", postTime: "2026-08-07 18:00", rowNumber: "2" },
  { id: "2", videoTitle: "Inspirational Quote #2", videoTranscript: "Innovation distinguishes between a leader and a follower.", status: "Success", youtubeLink: "https://youtube.com/watch?v=def456", outputPath: "./vid_def456.mp4", postTime: "2026-08-07 17:55", rowNumber: "3" },
  { id: "3", videoTitle: "Life Quote #3", videoTranscript: "Stay hungry, stay foolish.", status: "Success", youtubeLink: "https://youtube.com/watch?v=ghi789", outputPath: "./vid_ghi789.mp4", postTime: "2026-08-07 17:50", rowNumber: "4" },
  { id: "4", videoTitle: "Success Quote #4", videoTranscript: "Success is not final, failure is not fatal.", status: "Failed", rowNumber: "5" },
  { id: "5", videoTitle: "Wisdom Quote #5", videoTranscript: "The best time to plant a tree was 20 years ago.", status: "Success", youtubeLink: "https://youtube.com/watch?v=jkl012", outputPath: "./vid_jkl012.mp4", postTime: "2026-08-07 17:45", rowNumber: "6" },
]

export default function VideoLogs() {
  const [logs] = useState<VideoLog[]>(mockLogs)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredLogs = logs.filter((log) =>
    log.videoTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
    log.status.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Success": return "default"
      case "Pending": return "secondary"
      case "Failed": return "destructive"
      default: return "outline"
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Video Logs</h2>
        <p className="text-muted-foreground">History of generated and uploaded videos</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Generated</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{logs.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Successfully Uploaded</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{logs.filter(l => l.status === "Success").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Failed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{logs.filter(l => l.status === "Failed").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {logs.length > 0 ? Math.round((logs.filter(l => l.status === "Success").length / logs.length) * 100) : 0}%
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Video History</CardTitle>
              <CardDescription>{filteredLogs.length} records</CardDescription>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Row #</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Transcript</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Post Time</TableHead>
                <TableHead>YouTube Link</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-mono">{log.rowNumber}</TableCell>
                  <TableCell className="font-medium max-w-[200px] truncate">{log.videoTitle}</TableCell>
                  <TableCell className="max-w-[300px] truncate text-muted-foreground">{log.videoTranscript}</TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(log.status)}>{log.status}</Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">{log.postTime || "-"}</TableCell>
                  <TableCell>
                    {log.youtubeLink ? (
                      <a href={log.youtubeLink} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-blue-500 hover:underline">
                        Watch <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
