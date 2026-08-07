import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save, Globe, PlayCircle, FileText, CheckCircle, Link2, ExternalLink } from "lucide-react"
import { WEBHOOK_URL } from "@/lib/n8n-api"

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
          <TabsTrigger value="ngrok">ngrok</TabsTrigger>
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
        <TabsContent value="ngrok">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Link2 className="h-4 w-4" />
                ngrok Tunnel
              </CardTitle>
              <CardDescription>Public webhook URL for n8n</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Webhook URL</label>
                <Input
                  value={WEBHOOK_URL}
                  readOnly
                  placeholder="Not configured"
                />
                {WEBHOOK_URL && (
                  <a
                    href={WEBHOOK_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-500 hover:underline flex items-center gap-1"
                  >
                    Open webhook URL <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Auth Token</label>
                <Input
                  type="password"
                  value="36cQXTHuoRnyna1ZDgWk2sZnURn_3dtV7ory39KFT93SSQ9GG"
                  readOnly
                />
              </div>
              <div className="text-xs text-muted-foreground bg-muted p-3 rounded-md">
                <p className="font-medium mb-1">Quick Start</p>
                <p>Run <code className="bg-background px-1 rounded">npm run ngrok</code> to start the tunnel for the dev server (port 5173).</p>
                <p className="mt-1">Run <code className="bg-background px-1 rounded">npm run ngrok:n8n</code> to tunnel n8n (port 5678).</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
