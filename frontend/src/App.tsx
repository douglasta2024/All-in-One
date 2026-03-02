import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Chat from './components/tools/YoutubeToNotion/Chat'

type ToolId = 'youtube-to-notion'

const TOOLS: { id: ToolId; label: string }[] = [
  { id: 'youtube-to-notion', label: 'YouTube → Notion' },
]

export default function App() {
  const [activeTool, setActiveTool] = useState<ToolId>('youtube-to-notion')
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="h-screen flex overflow-hidden bg-canvas text-ink-1 font-sans antialiased">
      <Sidebar
        tools={TOOLS}
        activeTool={activeTool}
        onSelectTool={setActiveTool}
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed(c => !c)}
      />
      <main className="flex-1 flex flex-col overflow-hidden min-w-0">
        {activeTool === 'youtube-to-notion' && <Chat />}
      </main>
    </div>
  )
}
