import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Plus, Search, Trash2, Edit, ExternalLink } from "lucide-react"

interface VideoPool {
  id: string
  videoPath: string
  status: string
  internalPath?: string
  rowNumber: string
}

const mockVideos: VideoPool[] = [
  { id: "1", videoPath: "https://youtube.com/watch?v=dQw4w9WgXcQ", status: "Pending", rowNumber: "2" },
  { id: "2", videoPath: "https://youtube.com/watch?v=abc123", status: "Success", rowNumber: "3", internalPath: "./footage/abc123.mp4" },
  { id: "3", videoPath: "https://youtube.com/watch?v=xyz789", status: "Pending", rowNumber: "4" },
  { id: "4", videoPath: "https://youtube.com/watch?v=def456", status: "Success", rowNumber: "5", internalPath: "./footage/def456.mp4" },
  { id: "5", videoPath: "https://youtube.com/watch?v=ghi012", status: "Pending", rowNumber: "6" },
]

export default function VideoPools() {
  const [videos] = useState<VideoPool[]>(mockVideos)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredVideos = videos.filter((v) =>
    v.videoPath.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.status.toLowerCase().includes(searchQuery.toLowerCase())
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Video Pools</h2>
          <p className="text-muted-foreground">Manage your source video assets from YouTube</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Video
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>All Videos</CardTitle>
              <CardDescription>{filteredVideos.length} videos in pool</CardDescription>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search videos..."
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
                <TableHead>Video URL</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Internal Path</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredVideos.map((video) => (
                <TableRow key={video.id}>
                  <TableCell className="font-mono">{video.rowNumber}</TableCell>
                  <TableCell>
                    <a href={video.videoPath} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-blue-500 hover:underline">
                      {video.videoPath.length > 50 ? video.videoPath.slice(0, 50) + "..." : video.videoPath}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(video.status)}>{video.status}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{video.internalPath || "-"}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button variant="ghost" size="icon">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="text-destructive">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
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
