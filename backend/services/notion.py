"""
Notion API integration.
Writes structured notes to the database defined in SKILL.md Section 7.
"""
import os
import re
from datetime import date
from notion_client import Client

_CITATION_RE = re.compile(r"\s*\[\d+\]")

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        api_key = os.environ.get("NOTION_API_KEY")
        if not api_key:
            raise ValueError("NOTION_API_KEY is not set in environment")
        _client = Client(auth=api_key)
    return _client


def _heading(text: str) -> dict:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def _paragraph(label: str = "", value: str = "") -> dict:
    """Plain paragraph, or a labeled paragraph with bold label when label is given."""
    if label:
        rich_text = [
            {"type": "text", "text": {"content": f"{label}: "}, "annotations": {"bold": True}},
            {"type": "text", "text": {"content": value}},
        ]
    else:
        rich_text = [{"type": "text", "text": {"content": value}}] if value else []
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text},
    }



def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


_TEXT_LIMIT = 2000


def _chunks(text: str) -> list[str]:
    """Split text into segments of at most _TEXT_LIMIT characters."""
    return [text[i:i + _TEXT_LIMIT] for i in range(0, len(text), _TEXT_LIMIT)] or [""]


def _heading3(text: str) -> dict:
    clean = _CITATION_RE.sub("", text).replace("**", "").strip()
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": clean[:_TEXT_LIMIT]}}]},
    }


def _block_rt(block_type: str, rich_text: list[dict]) -> dict:
    return {"object": "block", "type": block_type, block_type: {"rich_text": rich_text}}


def _parse_rich_text(text: str) -> list[dict]:
    """Parse inline **bold** markers and strip [N] citations into Notion rich_text spans."""
    text = _CITATION_RE.sub("", text)
    if not text.strip():
        return []
    spans = []
    for i, part in enumerate(text.split("**")):
        if not part:
            continue
        is_bold = (i % 2 == 1)
        for chunk in _chunks(part):
            span: dict = {"type": "text", "text": {"content": chunk}}
            if is_bold:
                span["annotations"] = {"bold": True}
            spans.append(span)
    return spans


def _content_blocks(text: str) -> list[dict]:
    """Convert NotebookLM markdown output into Notion blocks.
    Handles: ## / ### headings, - / * / • bullets, 1. numbered lists,
    **bold** inline, [N] citation stripping, and 2000-char chunking."""
    blocks = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Markdown headings (any level) → heading_3
        if re.match(r"^#{1,6}\s", line):
            blocks.append(_heading3(re.sub(r"^#{1,6}\s+", "", line)))
        # Bullet: -, •, or * followed by one or more spaces
        elif re.match(r"^[-•*]\s+", line):
            rt = _parse_rich_text(re.sub(r"^[-•*]\s+", "", line))
            if rt:
                blocks.append(_block_rt("bulleted_list_item", rt))
        # Numbered list: 1. / 2. etc.
        elif re.match(r"^\d+\.\s+", line):
            rt = _parse_rich_text(re.sub(r"^\d+\.\s+", "", line))
            if rt:
                blocks.append(_block_rt("numbered_list_item", rt))
        # Regular paragraph with possible inline bold
        else:
            rt = _parse_rich_text(line)
            if rt:
                blocks.append(_block_rt("paragraph", rt))
    return blocks or [_paragraph()]


def _section(heading: str, content: str) -> list[dict]:
    return [_heading(heading)] + _content_blocks(content)


def _build_page_content(metadata: dict, summaries: dict) -> list[dict]:
    """Build Notion block content from AI-generated summaries."""
    title = metadata.get("title", "")
    channel = metadata.get("uploader", "")
    url = metadata.get("webpage_url", "")
    today = date.today().isoformat()

    meta_blocks = [
        _heading("Metadata"),
        _paragraph("Title", title),
        _paragraph("Channel", channel),
        _paragraph("URL", url),
        _paragraph("Date Watched", today),
        _divider(),
    ]

    section_blocks = []
    for name, content in summaries.items():
        section_blocks += _section(name, content)

    all_blocks = meta_blocks + section_blocks
    return all_blocks[:100]  # Notion API limit per request


def write_to_notion(metadata: dict, summaries: dict, category: str) -> str:
    """
    Create a new page in the Notion database.
    Returns the URL of the created page.
    """
    client = _get_client()
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not database_id:
        raise ValueError("NOTION_DATABASE_ID is not set in environment")

    title = metadata.get("title", "Untitled")
    channel = metadata.get("uploader", "")
    url = metadata.get("webpage_url", "")
    today = date.today().isoformat()

    blocks = _build_page_content(metadata, summaries)

    response = client.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {"title": [{"text": {"content": title}}]},
            "Category": {"select": {"name": category}},
            "Channel": {"rich_text": [{"text": {"content": channel}}]},
            "URL": {"url": url},
            "Date Watched": {"date": {"start": today}},
        },
        children=blocks,
    )

    return response.get("url", "")
