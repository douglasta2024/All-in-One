import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from services.categorizer import detect_category
from services.youtube import fetch_metadata
from services.notebooklm import add_and_query
from services.notion import write_to_notion

router = APIRouter()


class ProcessRequest(BaseModel):
    url: str
    category: Optional[str] = None  # If None, auto-detect


async def event_stream(url: str, category: Optional[str]):
    def emit(event_type: str, **kwargs):
        data = {"type": event_type, **kwargs}
        return f"data: {json.dumps(data)}\n\n"

    try:
        # Step 1: Fetch metadata for category detection
        yield emit("progress", message="Fetching video metadata...")
        metadata = await asyncio.to_thread(fetch_metadata, url)

        # Step 2: Category detection or use provided
        if category is None:
            detected = detect_category(metadata)
            yield emit("category_detected",
                       category=detected,
                       title=metadata.get("title", ""),
                       channel=metadata.get("uploader", ""))
            # Wait — frontend will re-call with confirmed category
            return
        else:
            yield emit("progress", message=f"Category confirmed: {category}")

        # Step 3: Add to NotebookLM and generate notes
        yield emit("progress", message="Adding to NotebookLM and generating notes (this may take a minute)...")
        summaries = await asyncio.to_thread(add_and_query, url, category, metadata)

        # Step 6: Write to Notion
        yield emit("progress", message="Writing to Notion...")
        notion_url = await asyncio.to_thread(
            write_to_notion, metadata, summaries, category
        )

        yield emit("done", notionUrl=notion_url)

    except Exception as e:
        yield emit("error", message=str(e))


@router.post("/youtube-to-notion")
async def youtube_to_notion(req: ProcessRequest):
    return StreamingResponse(
        event_stream(req.url, req.category),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
