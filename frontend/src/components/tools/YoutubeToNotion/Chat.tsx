import { useState, useRef, useEffect, useCallback } from 'react'
import Message, { type Msg } from './Message'

let _id = 0
const nextId = () => ++_id

// ——— SSE Streaming ———————————————————————————————————————————————————

async function streamProcess(
  url: string,
  category: string | null,
  onEvent: (event: Record<string, unknown>) => void,
  signal: AbortSignal,
) {
  const res = await fetch('/api/youtube-to-notion', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, category }),
    signal,
  })

  if (!res.ok || !res.body) {
    throw new Error(`Server error ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const dataLine = part.split('\n').find(l => l.startsWith('data: '))
      if (!dataLine) continue
      try {
        onEvent(JSON.parse(dataLine.slice(6)))
      } catch {
        // skip malformed
      }
    }
  }
}

// ——— Component ——————————————————————————————————————————————————————

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [processing, setProcessing] = useState(false)

  // Stable refs to avoid stale closures
  const currentUrlRef = useRef('')
  const videoTitleRef = useRef('')
  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Cleanup on unmount
  useEffect(() => () => { abortRef.current?.abort() }, [])

  // ——— State helpers

  const addMsg = useCallback((msg: Msg) => {
    setMessages(prev => [...prev, msg])
  }, [])

  const sealLastProgress = useCallback(() => {
    setMessages(prev =>
      prev.map((m, i) =>
        i === prev.length - 1 && m.kind === 'progress'
          ? { ...m, completed: true }
          : m
      )
    )
  }, [])

  // ——— Core streaming logic

  const startStream = useCallback(async (url: string, category: string | null) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setProcessing(true)

    try {
      await streamProcess(url, category, (event) => {
        const type = event.type as string

        if (type === 'progress') {
          setMessages(prev => {
            // Seal previous progress if any
            const sealed = prev.map((m, i) =>
              i === prev.length - 1 && m.kind === 'progress'
                ? { ...m, completed: true }
                : m
            )
            return [...sealed, {
              kind: 'progress' as const,
              id: nextId(),
              text: event.message as string,
              completed: false,
            }]
          })
        }

        else if (type === 'category_detected') {
          const title = event.title as string
          videoTitleRef.current = title
          addMsg({
            kind: 'category',
            id: nextId(),
            detected: event.category as string,
            title,
            channel: event.channel as string,
          })
          setProcessing(false)
          // Return — user must confirm category before continuing
        }

        else if (type === 'done') {
          sealLastProgress()
          addMsg({
            kind: 'success',
            id: nextId(),
            notionUrl: event.notionUrl as string,
            title: videoTitleRef.current,
          })
          setProcessing(false)
        }

        else if (type === 'error') {
          sealLastProgress()
          addMsg({
            kind: 'error',
            id: nextId(),
            text: event.message as string,
          })
          setProcessing(false)
        }
      }, controller.signal)

    } catch (err) {
      if ((err as Error).name === 'AbortError') return
      sealLastProgress()
      addMsg({
        kind: 'error',
        id: nextId(),
        text: err instanceof Error ? err.message : 'Unexpected error',
      })
      setProcessing(false)
    }
  }, [addMsg, sealLastProgress])

  // ——— User actions

  const handleSubmit = useCallback(() => {
    const url = input.trim()
    if (!url || processing) return

    currentUrlRef.current = url
    setInput('')
    addMsg({ kind: 'user', id: nextId(), text: url })
    startStream(url, null)
  }, [input, processing, addMsg, startStream])

  const handleCategorySelect = useCallback((category: string) => {
    addMsg({ kind: 'user', id: nextId(), text: category })
    startStream(currentUrlRef.current, category)
  }, [addMsg, startStream])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSubmit()
    }
  }

  // ——— Render

  return (
    <div className="flex flex-col h-full">

      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-white/[0.07]">
        <h1 className="text-sm font-semibold text-ink-1 tracking-tight">YouTube → Notion</h1>
        <p className="text-xs text-ink-3 mt-0.5">Summarize any YouTube video into your Notion database</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 scroll-smooth">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-2.5 max-w-2xl mx-auto">
            {messages.map(msg => (
              <Message
                key={msg.id}
                msg={msg}
                onCategorySelect={handleCategorySelect}
              />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex-shrink-0 px-6 py-4 border-t border-white/[0.07]">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={processing}
            placeholder="Paste a YouTube URL..."
            className="
              flex-1 bg-pit border border-white/[0.08] rounded-lg
              px-4 py-2.5 text-sm text-ink-1
              placeholder:text-ink-4
              focus:outline-none focus:border-signal/40 focus:ring-1 focus:ring-signal/20
              disabled:opacity-40
              transition-colors font-mono
            "
          />
          <button
            onClick={handleSubmit}
            disabled={processing || !input.trim()}
            className="
              flex-shrink-0 px-4 py-2.5 rounded-lg text-sm font-medium
              flex items-center gap-2
              bg-signal hover:bg-signal/85
              disabled:opacity-40 disabled:cursor-not-allowed
              text-white transition-colors
            "
          >
            {processing ? <Spinner /> : <SendIcon />}
            <span>{processing ? 'Processing' : 'Send'}</span>
          </button>
        </div>
      </div>

    </div>
  )
}

// ——— Sub-components ————————————————————————————————————————————————

function EmptyState() {
  return (
    <div className="h-full flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <div className="w-11 h-11 rounded-xl bg-signal/[0.08] border border-signal/[0.15] flex items-center justify-center mx-auto mb-4">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="text-signal/70">
            <rect x="2" y="4" width="13" height="12" rx="2" stroke="currentColor" strokeWidth="1.3" />
            <path d="M15 7.5l3-1.5v8l-3-1.5V7.5z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
            <path d="M7 9l4 2-4 2V9z" fill="currentColor" />
          </svg>
        </div>
        <p className="text-sm font-medium text-ink-2">Paste a YouTube URL to begin</p>
        <p className="text-xs text-ink-3 mt-1.5 leading-relaxed">
          Audio is transcribed locally — nothing sent to the cloud
        </p>
      </div>
    </div>
  )
}

function Spinner() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="animate-spin">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.25" />
      <path d="M7 1.5a5.5 5.5 0 0 1 5.5 5.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function SendIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
