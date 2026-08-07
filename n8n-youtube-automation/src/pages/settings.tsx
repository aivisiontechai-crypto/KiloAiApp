import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save, Globe, PlayCircle, FileText, CheckCircle } from "lucide-react"

export default function Settings() {
  const [n8nUrl, setN8nUrl] = useState("http://localhost:5678")
  const [apiKey, setApiKey] = useState("")
  const [youtubeClientId, setYoutubeClientId] = useState("")
  const [googleSheetsId, setGoogleSheetsId] = useState("1vURUl23pR74p7ha9oo-YRe6pktXIn7bslGWHoLcUktg")
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-2xl font-bold">Settings</h2>
        <p className="text-muted-foreground">Configure n8n and external service integrations</p>
      </div>

      <Tabs defaultValue="n8n">
        <TabsList>
          <TabsTrigger value="n8n">n8n</TabsTrigger>
          <TabsTrigger value="youtube">YouTube</TabsTrigger>
          <TabsTrigger value="sheets">Google Sheets</TabsTrigger>
        </TabsList>
        <TabsContent value="n8n">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-4 w-4" />
                n8n Configuration
              </CardTitle>
              <CardDescription>Connect to your n8n instance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">n8n API URL</label>
                <Input
                  placeholder="http://localhost:5678"
                  value={n8nUrl}
                  onChange={(e) => setN8nUrl(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">API Key</label>
                <Input
                  type="password"
                  placeholder="Enter your n8n API key"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
              </div>
              <Button onClick={handleSave} className="w-full">
                {saved ? <><CheckCircle className="h-4 w-4 mr-2" /> Saved!</> : <><Save className="h-4 w-4 mr-2" /> Save Configuration</>}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="youtube">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PlayCircle className="h-4 w-4" />
                YouTube API
              </CardTitle>
              <CardDescription>YouTube Data API v3 credentials</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Client ID</label>
                <Input
                  placeholder="Enter YouTube Client ID"
                  value={youtubeClientId}
                  onChange={(e) => setYoutubeClientId(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Client Secret</label>
                <Input
                  type="password"
                  placeholder="Enter YouTube Client Secret"
                />
              </div>
              <Button onClick={handleSave} className="w-full">
                {saved ? <><CheckCircle className="h-4 w-4 mr-2" /> Saved!</> : <><Save className="h-4 w-4 mr-2" /> Save Configuration</>}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="sheets">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Google Sheets
              </CardTitle>
              <CardDescription>Spreadsheet configuration for data management</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Spreadsheet ID</label>
                <Input
                  placeholder="Enter Google Sheets ID"
                  value={googleSheetsId}
                  onChange={(e) => setGoogleSheetsId(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Service Account Email</label>
                <Input
                  placeholder="service-account@project.iam.gserviceaccount.com"
                />
              </div>
              <Button onClick={handleSave} className="w-full">
                {saved ? <><CheckCircle className="h-4 w-4 mr-2" /> Saved!</> : <><Save className="h-4 w-4 mr-2" /> Save Configuration</>}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
