"""
Notion API integration.
Writes structured notes to the database defined in SKILL.md Section 7.
"""
import os
from datetime import date
from notion_client import Client

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


def _bullet(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def _content_blocks(text: str) -> list[dict]:
    """Convert summary text into Notion blocks, rendering bullet lines as list items."""
    blocks = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith(("- ", "• ", "* ")):
            blocks.append(_bullet(line[2:]))
        else:
            blocks.append(_paragraph(value=line))
    return blocks or [_paragraph()]


def _section(heading: str, content: str) -> list[dict]:
    return [_heading(heading)] + _content_blocks(content)


def _build_page_content(category: str, metadata: dict, summaries: dict) -> list[dict]:
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

    if category == "Educational/Tutorial":
        sections = [
            "Summary",
            "Key Concepts",
            "Definitions & Terminology",
            "Takeaways",
        ]
    elif category == "Tech/Programming":
        sections = [
            "Summary",
            "Tools & Libraries",
            "Key Points & Implementation Notes",
            "Code Snippets & Commands",
            "Gotchas & Tips",
            "Takeaways",
        ]
    else:  # Stocks
        sections = [
            "Overview",
            "Tickers & Companies Mentioned",
            "Bull Arguments",
            "Bear Arguments",
            "Key Quotes",
            "Open Questions",
        ]

    section_blocks = []
    for name in sections:
        content = summaries.get(name, "")
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

    blocks = _build_page_content(category, metadata, summaries)

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
