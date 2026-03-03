import type { ReactNode } from 'react'

// ——— Types ————————————————————————————————————————————————————————————

export type Msg =
  | { kind: 'user';     id: number; text: string }
  | { kind: 'progress'; id: number; text: string; completed: boolean }
  | { kind: 'category'; id: number; detected: string; title: string; channel: string }
  | { kind: 'success';  id: number; notionUrl: string; title: string }
  | { kind: 'error';    id: number; text: string }

// ——— Shared Bubble ————————————————————————————————————————————————————

function BotBubble({ children, fault = false }: { children: ReactNode; fault?: boolean }) {
  return (
    <div
      className={`
        max-w-[72%] rounded-xl px-4 py-3 text-sm leading-relaxed border
        ${fault
          ? 'bg-fault/[0.08] border-fault/20'
          : 'bg-surface border-white/[0.07]'
        }
      `}
    >
      {children}
    </div>
  )
}

// ——— Message Variants ————————————————————————————————————————————————

function UserMessage({ msg }: { msg: Extract<Msg, { kind: 'user' }> }) {
  const isUrl = msg.text.startsWith('http')
  return (
    <div className="flex justify-end">
      <div className="max-w-[72%] bg-signal/[0.10] border border-signal/25 rounded-xl px-4 py-2.5">
        <p className={`text-sm text-signal break-all ${isUrl ? 'font-mono' : 'font-medium'}`}>
          {msg.text}
        </p>
      </div>
    </div>
  )
}

function ProgressMessage({ msg }: { msg: Extract<Msg, { kind: 'progress' }> }) {
  return (
    <div className="flex justify-start">
      <BotBubble>
        <div className="flex items-center gap-2.5">
          {msg.completed ? <DoneIcon /> : <PulseIcon />}
          <span className={msg.completed ? 'text-ink-3' : 'text-ink-2'}>
            {msg.text}
          </span>
        </div>
      </BotBubble>
    </div>
  )
}

const CATEGORIES = ['General', 'Technology', 'Stocks']

function CategoryMessage({
  msg,
  onSelect,
}: {
  msg: Extract<Msg, { kind: 'category' }>
  onSelect: (cat: string) => void
}) {
  return (
    <div className="flex justify-start">
      <BotBubble>
        <div className="space-y-3">
          <div>
            <p className="text-ink-1 text-sm font-medium leading-snug">"{msg.title}"</p>
            <p className="text-ink-3 text-xs mt-0.5">by {msg.channel}</p>
          </div>
          <div>
            <p className="text-ink-3 text-xs mb-2 font-medium tracking-wide uppercase" style={{ letterSpacing: '0.06em' }}>
              Confirm category
            </p>
            <div className="flex flex-wrap gap-1.5">
              {CATEGORIES.map(cat => {
                const isDetected = cat === msg.detected
                return (
                  <button
                    key={cat}
                    onClick={() => onSelect(cat)}
                    className={`
                      px-3 py-1.5 rounded-md text-xs font-medium border
                      transition-colors cursor-pointer
                      ${isDetected
                        ? 'bg-signal/[0.14] border-signal/35 text-signal'
                        : 'bg-white/[0.04] border-white/[0.09] text-ink-2 hover:bg-white/[0.08] hover:text-ink-1 hover:border-white/[0.14]'
                      }
                    `}
                  >
                    {cat}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </BotBubble>
    </div>
  )
}

function SuccessMessage({ msg }: { msg: Extract<Msg, { kind: 'success' }> }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[72%] bg-surface border border-done/[0.22] rounded-xl px-4 py-3.5">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5 w-5 h-5 rounded-full bg-done/[0.14] flex items-center justify-center">
            <svg width="10" height="8" viewBox="0 0 10 8" fill="none" className="text-done">
              <path d="M1 4l3 3 5-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-ink-1">Saved to Notion</p>
            {msg.title && (
              <p className="text-xs text-ink-2 mt-0.5 mb-3 leading-relaxed max-w-[280px]">
                {msg.title}
              </p>
            )}
            <a
              href={msg.notionUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-signal hover:text-signal/75 font-medium transition-colors"
            >
              Open in Notion
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                <path d="M2 8L8 2M8 2H4M8 2v4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

function ErrorMessage({ msg }: { msg: Extract<Msg, { kind: 'error' }> }) {
  return (
    <div className="flex justify-start">
      <BotBubble fault>
        <div className="flex items-start gap-2.5">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-fault mt-0.5 flex-shrink-0">
            <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.2" />
            <path d="M7 4.5v3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
            <circle cx="7" cy="9.5" r="0.6" fill="currentColor" />
          </svg>
          <span className="text-ink-2">{msg.text}</span>
        </div>
      </BotBubble>
    </div>
  )
}

// ——— Icons —————————————————————————————————————————————————————————

function DoneIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" className="text-done flex-shrink-0">
      <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" strokeWidth="1.1" strokeOpacity="0.4" />
      <path d="M4 6.5l2 2 3-3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function PulseIcon() {
  return (
    <span className="relative flex-shrink-0 w-2.5 h-2.5">
      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-signal opacity-40" />
      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-signal/60" />
    </span>
  )
}

// ——— Main Export ————————————————————————————————————————————————————

export default function Message({
  msg,
  onCategorySelect,
}: {
  msg: Msg
  onCategorySelect?: (category: string) => void
}) {
  switch (msg.kind) {
    case 'user':     return <UserMessage msg={msg} />
    case 'progress': return <ProgressMessage msg={msg} />
    case 'category': return <CategoryMessage msg={msg} onSelect={onCategorySelect ?? (() => {})} />
    case 'success':  return <SuccessMessage msg={msg} />
    case 'error':    return <ErrorMessage msg={msg} />
  }
}
