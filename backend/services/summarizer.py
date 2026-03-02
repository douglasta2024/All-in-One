"""
Local summarization using Ollama.
Calls the Ollama REST API to generate structured notes from a transcript.
"""
import os
import json
import httpx

OLLAMA_BASE_URL = "http://localhost:11434"

CATEGORY_SECTIONS = {
    "Educational/Tutorial": [
        "Summary",
        "Key Concepts",
        "Definitions & Terminology",
        "Takeaways",
    ],
    "Tech/Programming": [
        "Summary",
        "Tools & Libraries",
        "Key Points & Implementation Notes",
        "Code Snippets & Commands",
        "Gotchas & Tips",
        "Takeaways",
    ],
    "Stocks": [
        "Overview",
        "Tickers & Companies Mentioned",
        "Bull Arguments",
        "Bear Arguments",
        "Key Quotes",
        "Open Questions",
    ],
}


def _build_prompt(transcript: str, category: str, metadata: dict) -> str:
    sections = CATEGORY_SECTIONS.get(category, CATEGORY_SECTIONS["Educational/Tutorial"])
    sections_json = {s: "" for s in sections}
    title = metadata.get("title", "")
    channel = metadata.get("uploader", "")

    return f"""You are a note-taking assistant. Analyze the following YouTube video transcript and extract structured notes.

Video: {title}
Channel: {channel}
Category: {category}

Transcript:
{transcript[:30000]}

Fill in the following sections based on the transcript. Respond ONLY with a valid JSON object — no explanation, no markdown code fences.

Required JSON format:
{json.dumps(sections_json, indent=2)}

Rules:
- Use bullet points for lists (start each bullet with "- ")
- Keep each section concise and relevant
- If a section has no applicable content, write "N/A"
"""


def _extract_json(raw: str) -> dict:
    """Try multiple strategies to extract a JSON object from model output."""
    # Strategy 1: direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip markdown code fences (```json ... ``` or ``` ... ```)
    stripped = raw
    for fence in ("```json", "```"):
        if fence in stripped:
            stripped = stripped.split(fence, 1)[-1]
            stripped = stripped.rsplit("```", 1)[0].strip()
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass

    # Strategy 3: find outermost { ... }
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass

    return {}


def summarize(transcript: str, category: str, metadata: dict) -> dict[str, str]:
    """
    Summarize a transcript into category-specific sections using a local Ollama model.
    Returns a dict mapping section name -> generated content.
    """
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    prompt = _build_prompt(transcript, category, metadata)

    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300.0,
    )
    response.raise_for_status()

    raw = response.json().get("response", "")

    summaries = _extract_json(raw)

    # Fallback: if JSON parsing failed entirely, put the raw output under Summary
    if not summaries:
        sections = CATEGORY_SECTIONS.get(category, CATEGORY_SECTIONS["Educational/Tutorial"])
        summaries = {s: "" for s in sections}
        summaries[sections[0]] = raw.strip() or "Could not generate summary."

    return summaries
