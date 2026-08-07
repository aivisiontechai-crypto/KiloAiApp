import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AppShell } from "@/components/layout/app-shell"
import Dashboard from "@/pages/dashboard"
import VideoPools from "@/pages/video-pools"
import MusicPools from "@/pages/music-pools"
import VideoLogs from "@/pages/video-logs"
import Execute from "@/pages/execute"
import Settings from "@/pages/settings"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="video-pools" element={<VideoPools />} />
          <Route path="music-pools" element={<MusicPools />} />
          <Route path="video-logs" element={<VideoLogs />} />
          <Route path="execute" element={<Execute />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
