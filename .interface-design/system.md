# Interface Design System — All-in-One

## Direction

**Product:** Multi-tool hub. First tool: YouTube → Notion knowledge capture.

**User:** Developer / knowledge worker at their desk, clipboard URL ready. Execution mode — not exploring. They want to offload cognitive work, then get out.

**Feel:** Focused pipeline. Quiet and capable. Like a terminal that went to therapy. Dense enough to feel powerful, calm enough not to interrupt flow.

---

## Palette

| Token | Value | Role |
|---|---|---|
| `canvas` | `#111318` | Base layer — blue-shifted dark, not neutral gray |
| `surface` | `#181b22` | Raised surface — bubbles, cards, elevated elements |
| `raised` | `#1f2332` | Further elevated — hover states, active items |
| `pit` | `#0c0f14` | Recessed — inputs receive content, they're inset |
| `signal` | `#bf6a60` | Accent — YouTube red at half saturation |
| `done` | `#5b9e7c` | Success — muted sage green |
| `fault` | `#c46060` | Error — muted red |
| `ink-1` | `#e4e6ed` | Primary text |
| `ink-2` | `#8b92a5` | Secondary text |
| `ink-3` | `#545c70` | Tertiary / labels |
| `ink-4` | `#2a2f3d` | Muted / placeholder |

Defined in `tailwind.config.js` under `theme.extend.colors`. Use opacity modifiers freely: `bg-signal/10`, `border-fault/20`, `bg-white/[0.07]`, etc.

---

## Depth Strategy

**Borders-only.** No shadows. This is a dense technical tool — shadows would soften it wrong.

- Standard border: `border-white/[0.07]`
- Emphasis border: `border-white/[0.10]` – `border-white/[0.14]`
- Interactive focus: `ring-1 ring-signal/20` + `border-signal/40`
- Semantic borders: `border-done/[0.22]`, `border-fault/20`, `border-signal/25`

Sidebar uses same canvas background as main content. Separation by right border only (`border-r border-white/[0.07]`).

---

## Spacing

Base unit: **8px**. Scale: 4 / 8 / 12 / 16 / 24 / 32 / 48.

Use Tailwind's built-in scale (1 = 4px). Prefer `p-4` (16px), `gap-2.5` (10px), `px-6` (24px) for section padding.

---

## Typography

Font: `Inter, system-ui, sans-serif` — function over personality.

| Role | Size | Weight | Notes |
|---|---|---|---|
| Heading | `text-sm` (14px) | `font-semibold` | Tool names, section titles |
| Body | `text-sm` (14px) | `font-normal` | Message content |
| Label | `text-xs` (12px) | `font-medium` | Category labels, metadata |
| Monospace | `font-mono` | — | URLs, code |

---

## Border Radius

- Inputs, buttons: `rounded-lg` (8px)
- Message bubbles: `rounded-xl` (12px)
- Icon containers: `rounded-md` (6px) or `rounded-lg` (8px)
- Status dots / pills: `rounded-full`

---

## Component Patterns

### Sidebar
- Same background as canvas (`bg-canvas`)
- Separated by `border-r border-white/[0.07]` only
- Expanded: `w-52`, collapsed: `w-14`
- Transition: `transition-[width] duration-200 ease-in-out`
- Active tool: `bg-signal/10 text-signal`
- Hover: `hover:bg-white/[0.04] hover:text-ink-1`
- Labels collapse with `max-w-0 opacity-0` → `max-w-[140px] opacity-100`

### Chat Bubbles
- User (right): `bg-signal/[0.10] border border-signal/25 rounded-xl`
  - URL text: `font-mono text-signal`
  - Selection text: `font-medium text-signal`
- Bot (left): `bg-surface border border-white/[0.07] rounded-xl`
- Error (left): `bg-fault/[0.08] border border-fault/20 rounded-xl`
- Success (left): `bg-surface border border-done/[0.22] rounded-xl`
- Max width: `max-w-[72%]`
- Padding: `px-4 py-3`

### Progress Pipeline (Signature)
Each processing stage is its own bubble. Current stage: pulsing signal-colored dot (animate-ping). Completed stage: sealed with a ringed checkmark in `done` color. The pipeline trace stays visible — you see the work.

### Category Chips
Three chips per confirmation message. Detected category pre-highlighted with `bg-signal/[0.14] border-signal/35 text-signal`. Others: `bg-white/[0.04] border-white/[0.09] text-ink-2`.

### Input Area
- Background: `bg-pit` (inset/recessed)
- Border: `border border-white/[0.08]`
- Focus: `focus:border-signal/40 focus:ring-1 focus:ring-signal/20`
- Send button: `bg-signal hover:bg-signal/85 text-white`
- Processing: spinner replaces send icon, button disabled

### Empty State
Centered icon container `w-11 h-11 rounded-xl bg-signal/[0.08] border border-signal/[0.15]` with signal-colored icon at 70% opacity. Two-line description.

---

## Iconography

Inline SVG only — no icon library. One consistent stroke weight: `strokeWidth="1.3"` to `strokeWidth="1.5"`. `currentColor` for all paths. Icons are 13–20px.

---

## SSE Pattern

Use `fetch` (not `EventSource`) for POST-based SSE streams. Parse `data: {json}\n\n` manually from `ReadableStream`. Store `AbortController` in a ref for cleanup.

---

## Signature

**The pipeline trace.** Progress messages are not a loading spinner — they're a live audit trail. Each stage seals with a checkmark when the next begins. The user watches their work being done, step by step.
