---
name: notion-summary
description: Generate notes from a Youtube video and put those notes into Notion, with category-aware templates.
---

# YouTube → Notion Notes Skill — Reference Document

This document defines the behavior, preferences, and conventions for a skill that automatically converts YouTube videos into structured Notion notes. Note structure adapts based on the detected video category.

---

## 1. Input

- **Primary input:** A YouTube URL (single video or playlist).
- **Transcript method:** Use `yt-dlp` to download the audio, then transcribe with **Whisper** (local transcription). Do not rely on YouTube's auto-generated captions.

---

## 2. Output Destination

- **Target:** A single Notion database housing all notes across all categories.
- **Database schema:** See Section 8.
- **Each video becomes one database entry** (a page inside the database), with its properties filled and content written into the page body.
- **If the database doesn't exist yet:** Create it automatically using the schema in Section 8, but notify the user that it was newly created and confirm the parent page to place it under.

---

## 3. Language

- Always produce notes in **English**, regardless of the video's source language. Translate as needed.

---

## 4. Category Detection & Confirmation

Before transcribing or writing any notes, the skill must determine the video category.

### Step 1 — Auto-detect
Use the video's title, channel name, and description (retrieved via `yt-dlp` metadata, no transcription needed yet) to infer the category. Apply the following logic:

| Signals | Likely Category |
|---|---|
| Words like "tutorial", "how to", "guide", "learn", "course", "explained" | Educational/Tutorial |
| Words like "Python", "JavaScript", "code", "programming", "dev", "API", "build", "deploy", tech tool names | Tech/Programming |
| Words like "stock", "ticker", "bull", "bear", "earnings", "market", "invest", "trade", "buy", "sell", "valuation", channel names known to be finance-focused | Stocks |

### Step 2 — Confirm with user
After detecting, always pause and present:

```
Detected category: [Category]
Video: "[Title]" by [Channel]

Is this correct?
  [1] Yes, proceed
  [2] No — change to: Educational/Tutorial / Tech/Programming / Stocks
```

Do not begin transcription until the user confirms.

---

## 5. Category-Specific Note Templates

Use the confirmed category to select the appropriate template below. Do not use sections from other templates.

---

### 5A. Educational/Tutorial Template

**Goal:** Capture only what is genuinely useful to learn or reference later. Aggressively filter out filler, anecdotes, sponsorships, and tangential content.

**Sections (in order):**

1. **Metadata** — video title, channel, URL, date watched, tags/keywords
2. **Summary** — 1–2 paragraph plain-English overview of what this video teaches and who it's for
3. **Key Concepts** — the core ideas, principles, or mental models introduced. Each concept should be written as: *Concept name* → clear explanation in your own words. Prioritize depth over breadth — only include concepts that matter.
4. **Definitions & Terminology** — domain-specific terms the viewer needs to understand, written as a simple glossary
5. **Takeaways** — 3–7 bullet points of the most important things to remember or apply

Omit any section that has no substantive content. Skip sponsorships, personal anecdotes, and off-topic digressions entirely — do not note that they were skipped.

---

### 5B. Tech/Programming Template

**Goal:** Serve as a practical reference. Prioritize completeness for technical details — someone should be able to follow along or replicate using these notes alone.

**Sections (in order):**

1. **Metadata** — video title, channel, URL, date watched, tags/keywords
2. **Summary** — 1–2 paragraph overview of what is being built, demonstrated, or explained, and the problem it solves
3. **Tools & Libraries** — a quick-reference list of every tool, library, framework, or service mentioned. Format:
   - `tool-name` — what it does, why it was used here, any version info if mentioned
4. **Key Points & Implementation Notes** — the main technical steps, decisions, and explanations covered in the video. Written as clear, ordered notes (not a transcript). Include the *why* behind decisions, not just the *what*.
5. **Code Snippets & Commands** — all code, CLI commands, config files, or technical specifics, preserved exactly in fenced code blocks with language tags
6. **Gotchas & Tips** — any warnings, common mistakes, non-obvious behaviors, or performance notes the presenter mentions
7. **Takeaways** — concise closing synthesis of what was covered and what to do or explore next

---

### 5C. Stocks Template

**Goal:** Capture and critically frame the buy/sell arguments made in the video so they can be evaluated and acted on later with independent research.

**Sections (in order):**

1. **Metadata** — video title, channel, URL, date watched, tags/keywords
2. **Overview** — 1 paragraph on what stocks/sectors this video covers and the presenter's overall stance (bullish/bearish/neutral)
3. **Tickers & Companies Mentioned** — list every ticker and company discussed, with a one-line description of their role in the video (e.g. "NVDA — primary bullish thesis", "AMD — mentioned as competitor")
4. **Bull Arguments** — for each ticker where a bullish case is made: lay out the argument clearly and factually as the presenter made it. Include any catalysts, price targets, or timelines mentioned.
5. **Bear Arguments** — for each ticker where a bearish or risk case is made: same treatment as above. If the presenter didn't address bear cases, note that explicitly.
6. **Validity Assessment Prompts** — for each major argument, generate 2–3 specific research questions the user should investigate to verify or challenge the claim. Examples: "Check whether Q3 earnings confirmed the revenue growth thesis", "Verify the market size figure cited — what was the source?" These are not conclusions — they are prompts for the user's own follow-up research.
7. **Key Quotes** — verbatim quotes from the presenter that are particularly bold, specific, or actionable (price targets, direct recommendations, strong claims)
8. **Open Questions** — anything left unresolved, assumed without evidence, or worth digging into that the video didn't address

---

## 6. Special Content Handling

| Element | Behavior |
|---|---|
| Code / commands | Preserve exactly in fenced code blocks with language tag (Tech template only) |
| Definitions | Capture the speaker's own explanation where possible |
| Quotes | Verbatim; note speaker name if identifiable |
| Sponsorships / ads | Always skip entirely, never mention |
| Filler / off-topic | Skip in all templates; aggressively in Educational |

---

## 7. Notion Database Schema

The skill writes to a single database. Create it with the following properties:

| Property Name | Type | Notes |
|---|---|---|
| Title | Title | Video title |
| Category | Select | Options: `Educational/Tutorial`, `Tech/Programming`, `Stocks` |
| Channel | Text | YouTube channel name |
| URL | URL | YouTube video URL |
| Date Watched | Date | Date the skill was run |
| Tags | Multi-select | Keywords extracted from video metadata and content |
| Status | Select | Options: `Done`, `To Revisit` — default to `Done` on creation |

All other content (summaries, key points, code, arguments, etc.) goes into the **page body** using the appropriate template from Section 5.

---

## 8. Error Handling & Edge Cases

### Transcription failure
Stop and ask the user how to proceed — do not attempt to guess or partially continue.

### Very long videos (2+ hours)
- Warn the user before starting that processing may take a while.
- Process in logical chunks (e.g. by chapter or fixed time windows).
- Still produce a single unified Notion page with the full template.

### Playlists
- Ask the user upfront: should each video get its own Notion database entry, or be combined into one?
- If separate entries: process each video individually through the full pipeline.
- If combined: note the video title/URL at the start of each video's section within a single page.

### Videos with no recoverable transcript
- Notify the user clearly and ask how they'd like to proceed (skip, try different source, manually provide transcript).

### Category is ambiguous
- If the auto-detection is uncertain between two categories, say so explicitly and ask the user to choose before proceeding.

---

## 9. Pre-Flight Checklist

Before executing any part of the skill, Claude must run through this checklist. Stop and ask the user for anything missing before continuing.

### Required Credentials

| Key | Where It's Used | Env Var Name |
|---|---|---|
| Notion API key | Writing notes to Notion | `NOTION_API_KEY` |

### Required Runtime Inputs

| Input | Description |
|---|---|
| YouTube URL | The video or playlist to process |
| Notion database | The database ID or URL where notes should be saved (or confirm creation) |

### Checklist Behavior

- On startup, load a `.env` file from the working directory using `python-dotenv`.
- For each required credential, check if it's already set in the environment. If it is, proceed silently.
- If any credential is **missing**, prompt the user to provide it, then write it to the `.env` file for future runs.
- Do not proceed past the checklist until all items are confirmed.

### Validation Steps

1. **Notion API key** — make a test API call to confirm the key is valid and has write permissions.
2. **YouTube URL** — confirm it is reachable and valid. Warn if private or age-restricted.
3. **yt-dlp & Whisper** — confirm both are installed. If not, print clear installation instructions and exit.

---

## 10. Python Environment Notes

- Use `yt-dlp` for audio extraction and metadata retrieval.
- Use `openai-whisper` for local transcription.
- Use `notion-client` or direct HTTP for Notion API calls.
- Use `python-dotenv` for credential management.
- Structure the code in clear stages: `detect_category` → confirm → `download` → `transcribe` → `parse_by_category` → `write_to_notion`.
- Each stage should be a separate function with clear inputs/outputs and comments.
