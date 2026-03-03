"""
NotebookLM integration via the nlm CLI (notebooklm-mcp-cli).

Manages 3 shared notebooks (Stocks, Technology, General) and generates
video notes by adding YouTube sources and querying the notebook.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

# Locate nlm executable: check PATH first, then known uv install location
_NLM_CANDIDATES = [
    shutil.which("nlm"),
    str(Path.home() / ".local" / "bin" / "nlm.exe"),
    str(Path(os.environ.get("APPDATA", "")) / "uv" / "tools" / "notebooklm-mcp-cli" / "Scripts" / "nlm.exe"),
]
NLM_EXE = next((p for p in _NLM_CANDIDATES if p and Path(p).exists()), None)

# Category → notebook name mapping (categories now match notebook names)
CATEGORY_TO_NOTEBOOK = {
    "General": "General",
    "Technology": "Technology",
    "Stocks": "Stocks",
}

# Cache file for notebook IDs (stored next to main.py)
_CACHE_PATH = Path(__file__).parent.parent / ".notebooks.json"


def _run_nlm(*args: str, timeout: int = 120) -> str:
    """Run an nlm CLI command and return stdout. Raises RuntimeError on failure."""
    if not NLM_EXE:
        raise RuntimeError(
            "nlm executable not found. Install notebooklm-mcp-cli via uv and ensure it is on PATH."
        )
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"}
    result = subprocess.run(
        [NLM_EXE, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"nlm error: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def _load_cache() -> dict:
    if _CACHE_PATH.exists():
        with open(_CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(data: dict) -> None:
    with open(_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _list_notebooks() -> list[dict]:
    """Return list of all notebooks as dicts with 'id' and 'title'."""
    output = _run_nlm("notebook", "list", "--json")
    return json.loads(output.strip() or "[]")


def _get_or_create_notebook(name: str) -> str:
    """Return the notebook ID matching the given name, creating it if needed."""
    for nb in _list_notebooks():
        if nb.get("title", "").strip() == name:
            return nb["id"]

    # Not found — create it
    _run_nlm("notebook", "create", name)

    # Fetch updated list to get the new notebook's ID
    for nb in _list_notebooks():
        if nb.get("title", "").strip() == name:
            return nb["id"]

    raise RuntimeError(f"Failed to create or find notebook: {name}")


def ensure_notebooks() -> None:
    """
    Ensure all 3 category notebooks exist and cache their IDs.
    Call once on app startup.
    """
    cache = _load_cache()
    changed = False

    for notebook_name in set(CATEGORY_TO_NOTEBOOK.values()):
        if notebook_name not in cache:
            print(f"[NotebookLM] Resolving notebook: {notebook_name}")
            notebook_id = _get_or_create_notebook(notebook_name)
            cache[notebook_name] = notebook_id
            changed = True
            print(f"[NotebookLM] '{notebook_name}' → {notebook_id}")

    if changed:
        _save_cache(cache)


def _get_notebook_id(category: str) -> str:
    """Return the cached notebook ID for a category, resolving it if needed."""
    name = CATEGORY_TO_NOTEBOOK.get(category, "General")
    cache = _load_cache()
    if name in cache:
        return cache[name]

    # Cache miss — resolve and cache
    notebook_id = _get_or_create_notebook(name)
    cache[name] = notebook_id
    _save_cache(cache)
    return notebook_id


def _source_title_exists(notebook_id: str, title: str) -> bool:
    """Return True if a source with this title already exists in the notebook."""
    try:
        output = _run_nlm("source", "list", notebook_id, "--json")
        sources = json.loads(output.strip() or "[]")
        return any(s.get("title", "").strip() == title.strip() for s in sources)
    except Exception:
        return False  # On any error, assume it's new and attempt the add


def add_and_query(url: str, category: str, metadata: dict) -> dict:
    """
    Add a YouTube video to the appropriate NotebookLM notebook and query it for notes.
    Skips the add step if the video title is already present as a source.
    Returns {"Notes": <generated_notes_text>}.
    """
    notebook_id = _get_notebook_id(category)
    title = metadata.get("title", "this video")

    # Only add if not already in the notebook (YouTube sources have url=null, so match by title)
    if not _source_title_exists(notebook_id, title):
        _run_nlm("source", "add", notebook_id, "--youtube", url, "--wait", timeout=300)

    # Query the notebook, asking specifically about this video
    question = (
        f"Please provide comprehensive, well-organized notes for the video titled '{title}'. "
        "Only discuss this video. Do not reference other videos or sources in your response."
    )
    raw = _run_nlm("query", "notebook", notebook_id, question, timeout=120)

    # nlm query notebook outputs JSON: {"value": {"answer": "...", ...}}
    try:
        data = json.loads(raw.strip())
        notes = data.get("value", {}).get("answer", "").strip()
    except (json.JSONDecodeError, AttributeError):
        notes = raw.strip()  # fallback to raw text if parsing fails

    return {"Notes": notes or "No notes generated."}
