import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Plus, Search, Trash2, Edit, ExternalLink } from "lucide-react"

interface MusicPool {
  id: string
  musicPath: string
  status: string
  internalPath?: string
  rowNumber: string
}

const mockMusic: MusicPool[] = [
  { id: "1", musicPath: "https://youtube.com/watch?v=music1", status: "Success", rowNumber: "2", internalPath: "./footage/abc123.mp3" },
  { id: "2", musicPath: "https://youtube.com/watch?v=music2", status: "Pending", rowNumber: "3" },
  { id: "3", musicPath: "https://youtube.com/watch?v=music3", status: "Success", rowNumber: "4", internalPath: "./footage/def456.mp3" },
  { id: "4", musicPath: "https://youtube.com/watch?v=music4", status: "Pending", rowNumber: "5" },
  { id: "5", musicPath: "https://youtube.com/watch?v=music5", status: "Failed", rowNumber: "6" },
]

export default function MusicPools() {
  const [music] = useState<MusicPool[]>(mockMusic)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredMusic = music.filter((m) =>
    m.musicPath.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.status.toLowerCase().includes(searchQuery.toLowerCase())
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
          <h2 className="text-2xl font-bold">Music Pools</h2>
          <p className="text-muted-foreground">Manage your background music assets</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Music
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>All Music</CardTitle>
              <CardDescription>{filteredMusic.length} tracks in pool</CardDescription>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search music..."
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
                <TableHead>Music URL</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Internal Path</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredMusic.map((track) => (
                <TableRow key={track.id}>
                  <TableCell className="font-mono">{track.rowNumber}</TableCell>
                  <TableCell>
                    <a href={track.musicPath} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-blue-500 hover:underline">
                      {track.musicPath.length > 50 ? track.musicPath.slice(0, 50) + "..." : track.musicPath}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(track.status)}>{track.status}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{track.internalPath || "-"}</TableCell>
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
