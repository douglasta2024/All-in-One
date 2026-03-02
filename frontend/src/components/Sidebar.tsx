type Tool = { id: string; label: string }

type Props = {
  tools: Tool[]
  activeTool: string
  onSelectTool: (id: string) => void
  collapsed: boolean
  onToggleCollapse: () => void
}

export default function Sidebar({ tools, activeTool, onSelectTool, collapsed, onToggleCollapse }: Props) {
  return (
    <aside
      className={`
        flex-shrink-0 flex flex-col h-full
        bg-canvas border-r border-white/[0.07]
        transition-[width] duration-200 ease-in-out overflow-hidden
        ${collapsed ? 'w-14' : 'w-52'}
      `}
    >
      {/* Logo */}
      <div className={`flex items-center gap-2.5 px-3 py-4 ${collapsed ? 'justify-center' : ''}`}>
        <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-signal/10 border border-signal/20 flex items-center justify-center">
          <GridIcon />
        </div>
        <span
          className={`
            text-sm font-semibold text-ink-1 whitespace-nowrap overflow-hidden
            transition-all duration-200
            ${collapsed ? 'max-w-0 opacity-0' : 'max-w-[120px] opacity-100'}
          `}
        >
          All-in-One
        </span>
      </div>

      {/* Separator */}
      <div className="h-px bg-white/[0.05] mx-3" />

      {/* Tools */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {tools.map(tool => {
          const isActive = tool.id === activeTool
          return (
            <button
              key={tool.id}
              onClick={() => onSelectTool(tool.id)}
              title={collapsed ? tool.label : undefined}
              className={`
                w-full flex items-center gap-2.5 rounded-md text-sm
                transition-colors px-2.5 py-2
                ${isActive
                  ? 'bg-signal/10 text-signal'
                  : 'text-ink-2 hover:bg-white/[0.04] hover:text-ink-1'
                }
              `}
            >
              <span className="flex-shrink-0 w-4 h-4 flex items-center justify-center">
                <VideoIcon active={isActive} />
              </span>
              <span
                className={`
                  whitespace-nowrap overflow-hidden text-left
                  transition-all duration-200
                  ${collapsed ? 'max-w-0 opacity-0' : 'max-w-[140px] opacity-100'}
                `}
              >
                {tool.label}
              </span>
            </button>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <div className={`px-2 py-3 border-t border-white/[0.05] ${collapsed ? 'flex justify-center' : 'flex justify-end'}`}>
        <button
          onClick={onToggleCollapse}
          className="w-7 h-7 flex items-center justify-center rounded-md text-ink-3 hover:bg-white/[0.04] hover:text-ink-2 transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronIcon collapsed={collapsed} />
        </button>
      </div>
    </aside>
  )
}

function GridIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-signal">
      <rect x="1" y="1" width="5" height="5" rx="1" fill="currentColor" />
      <rect x="8" y="1" width="5" height="5" rx="1" fill="currentColor" opacity="0.6" />
      <rect x="1" y="8" width="5" height="5" rx="1" fill="currentColor" opacity="0.6" />
      <rect x="8" y="8" width="5" height="5" rx="1" fill="currentColor" opacity="0.3" />
    </svg>
  )
}

function VideoIcon({ active }: { active: boolean }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className={active ? 'text-signal' : 'text-ink-3'}>
      <rect x="1" y="2.5" width="9" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.1" />
      <path d="M10 5.5l3-1.5v6l-3-1.5V5.5z" stroke="currentColor" strokeWidth="1.1" strokeLinejoin="round" />
    </svg>
  )
}

function ChevronIcon({ collapsed }: { collapsed: boolean }) {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path
        d={collapsed ? 'M5 3.5l3 3-3 3' : 'M8 3.5L5 6.5l3 3'}
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
