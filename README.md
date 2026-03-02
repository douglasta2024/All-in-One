# All-in-One

A modular knowledge capture hub that automates converting multimedia content into structured Notion pages. Currently features a **YouTube → Notion** pipeline with streaming real-time feedback.

---

## Features

- **YouTube → Notion:** Paste a YouTube URL → get a fully structured Notion page with transcription, summary, and category-specific content templates
- **Fully local pipeline:** Audio transcribed on-device with Whisper, notes summarized with a local Ollama model — nothing sent to the cloud
- **Streaming UI:** Real-time progress updates via Server-Sent Events as each pipeline stage completes
- **Category-aware summaries:** Ollama fills in structured sections (Key Concepts, Takeaways, etc.) based on the detected video category

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Frontend  (React + Vite)              │
│                                                 │
│  App.tsx → Sidebar.tsx  (tool navigation)       │
│          → Chat.tsx     (streaming UI)          │
│          → Message.tsx  (5 message types)       │
└──────────────────┬──────────────────────────────┘
                   │  HTTP POST + SSE (via Vite proxy)
                   │  localhost:5173 → localhost:8000
┌──────────────────▼──────────────────────────────┐
│           Backend  (FastAPI + Uvicorn)          │
│                                                 │
│  main.py                                        │
│  routes/youtube_to_notion.py  ← POST endpoint  │
│                                                 │
│  services/                                      │
│    youtube.py      ← yt-dlp metadata + audio   │
│    transcriber.py  ← Whisper local transcription│
│    categorizer.py  ← keyword-based detection   │
│    summarizer.py   ← Ollama structured notes   │
│    notion.py       ← Notion API page creation  │
└─────────────────────────────────────────────────┘
```

### Pipeline Flow

1. User submits YouTube URL from the chat input
2. Backend fetches video metadata via `yt-dlp` → streams `progress` event
3. Category is auto-detected from title/channel/description keywords → streams `category_detected` event
4. User confirms or changes category in the UI
5. Frontend re-submits with confirmed category
6. Backend downloads audio and transcribes locally with **Whisper** (base model)
7. Transcript is sent to **Ollama** which generates structured notes for each section
8. Notion page is created with the AI-generated content → streams `done` event with page URL
9. Frontend displays a success card with a direct link to the Notion page

### Category Templates

| Category | Notion Sections |
|---|---|
| **Educational / Tutorial** | Summary, Key Concepts, Definitions, Takeaways |
| **Tech / Programming** | Summary, Tools & Stack, Implementation Notes, Code Snippets, Gotchas, Takeaways |
| **Stocks / Finance** | Ticker Analysis, Bull Arguments, Bear Arguments, Key Quotes, Validity Check |

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite 7, Tailwind CSS 3 |
| Backend | Python, FastAPI, Uvicorn, sse-starlette |
| YouTube | yt-dlp, FFmpeg |
| Transcription | openai-whisper (local) |
| Summarization | Ollama (local LLM, configurable model) |
| Notion | notion-client 2.2.1 |

---

## Prerequisites

- **Node.js** (v18+)
- **Python** (3.10+)
- **FFmpeg** — required by yt-dlp for audio extraction ([install guide](https://ffmpeg.org/download.html))
- **Ollama** — local LLM runner ([install guide](https://ollama.com/download)) with at least one model pulled (e.g. `ollama pull llama3.2`)
- A **Notion integration token** and a target **database ID**

---

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd All-in-one
```

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

**Frontend:**

```bash
cd frontend
npm install
```

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=...
OLLAMA_MODEL=llama3.2
```

To get these values:
1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations) and create an integration
2. Copy the **Internal Integration Token** as `NOTION_API_KEY`
3. Create a Notion database, share it with your integration, and copy the database ID from the URL as `NOTION_DATABASE_ID`

### 3. Set up the Notion database

Create a database in Notion with the following properties exactly as named:

| Property | Type | Notes |
|---|---|---|
| **Title** | Title | Page title (video title) |
| **Category** | Select | Options: `Educational/Tutorial`, `Tech/Programming`, `Stocks` |
| **Channel** | Rich text | YouTube channel name |
| **URL** | URL | Link to the original YouTube video |
| **Date Watched** | Date | Auto-set to today's date |

Each page created in the database also contains a structured body based on the video category:

**Educational / Tutorial pages include:**
- Metadata block (title, channel, URL, date)
- Summary
- Key Concepts
- Definitions & Terminology
- Takeaways
- Transcript excerpt (first 2000 characters)

**Tech / Programming pages include:**
- Metadata block
- Summary
- Tools & Libraries
- Key Points & Implementation Notes
- Code Snippets & Commands
- Gotchas & Tips
- Takeaways
- Transcript excerpt

**Stocks / Finance pages include:**
- Metadata block
- Overview
- Tickers & Companies Mentioned
- Bull Arguments
- Bear Arguments
- Validity Assessment Prompts
- Key Quotes
- Open Questions
- Transcript excerpt

Once the database is created, share it with your integration:
1. Open the database in Notion
2. Click `...` (top-right) → **Connections**
3. Search for your integration name and click **Confirm**

To verify everything is wired up correctly, run the test script:

```bat
cd backend
.venv\Scripts\activate
python test_notion.py
```

---

## Running

Start both servers in separate terminals:

**Terminal 1 — Backend:**

```bash
cd backend
.venv\Scripts\activate
python -m uvicorn main:app --reload
# Runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Project Structure

```
All-in-one/
├── backend/
│   ├── main.py                   # FastAPI app entrypoint
│   ├── requirements.txt
│   ├── .env.example              # Environment variable template
│   ├── routes/
│   │   └── youtube_to_notion.py  # POST /api/youtube-to-notion (SSE stream)
│   └── services/
│       ├── youtube.py            # yt-dlp metadata & audio download
│       ├── transcriber.py        # Whisper transcription
│       ├── categorizer.py        # Keyword-based category detection
│       └── notion.py             # Notion API page creation
├── frontend/
│   ├── index.html
│   ├── vite.config.ts            # Dev server + proxy to :8000
│   └── src/
│       ├── main.tsx              # React root
│       ├── App.tsx               # Tool router
│       └── components/
│           ├── Sidebar.tsx       # Collapsible tool navigation
│           └── tools/YoutubeToNotion/
│               ├── Chat.tsx      # SSE streaming chat UI
│               └── Message.tsx   # Message type components
└── .interface-design/
    └── system.md                 # Design system (colors, tokens, patterns)
```

---

## API Reference

### `POST /api/youtube-to-notion`

Streams Server-Sent Events as the pipeline runs.

**Request body:**

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "category": "Educational"   // optional; omit to trigger auto-detection
}
```

**SSE event types:**

| Event | Payload | Description |
|---|---|---|
| `progress` | `{ "step": "...", "status": "done" }` | A pipeline stage completed |
| `category_detected` | `{ "category": "..." }` | Auto-detected category (pauses for user confirmation) |
| `done` | `{ "url": "https://notion.so/..." }` | Notion page created successfully |
| `error` | `{ "message": "..." }` | Pipeline failure |

---

## Adding New Tools

The app is designed as an extensible hub:

1. Add a new component under `frontend/src/components/tools/<ToolName>/`
2. Register it in `App.tsx` tool router and `Sidebar.tsx` navigation
3. Add a new route under `backend/routes/<tool_name>.py`
4. Register the route in `backend/main.py`
