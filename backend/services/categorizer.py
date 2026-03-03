"""
Keyword-based category detection from video metadata.
Logic ported from .claude/skills/SKILL.md Section 4.
"""

EDUCATIONAL_KEYWORDS = {
    "tutorial", "how to", "guide", "learn", "learning", "course",
    "explained", "beginner", "introduction", "intro to", "basics",
    "deep dive", "walkthrough",
}

TECH_KEYWORDS = {
    "python", "javascript", "typescript", "react", "node", "nodejs",
    "code", "coding", "programming", "developer", "dev", "api",
    "build", "deploy", "deployment", "docker", "kubernetes", "aws",
    "cloud", "backend", "frontend", "fullstack", "database", "sql",
    "machine learning", "ai", "llm", "fastapi", "django", "flask",
    "git", "github", "cli", "terminal", "bash", "linux",
}

STOCKS_KEYWORDS = {
    "stock", "stocks", "ticker", "bull", "bear", "earnings",
    "market", "invest", "investing", "investment", "trade", "trading",
    "buy", "sell", "valuation", "portfolio", "dividend", "etf",
    "s&p", "nasdaq", "nyse", "ipo", "hedge fund", "wall street",
    "revenue", "earnings per share", "eps", "pe ratio", "price target",
}


def detect_category(metadata: dict) -> str:
    """
    Detect category from video title, channel, and description.
    Returns one of: 'General', 'Technology', 'Stocks'
    Defaults to 'General' when ambiguous.
    """
    haystack = " ".join([
        metadata.get("title", ""),
        metadata.get("uploader", ""),
        (metadata.get("description", "") or "")[:500],
    ]).lower()

    scores = {
        "General": 0,
        "Technology": 0,
        "Stocks": 0,
    }

    for kw in EDUCATIONAL_KEYWORDS:
        if kw in haystack:
            scores["General"] += 1

    for kw in TECH_KEYWORDS:
        if kw in haystack:
            scores["Technology"] += 1

    for kw in STOCKS_KEYWORDS:
        if kw in haystack:
            scores["Stocks"] += 1

    return max(scores, key=lambda k: scores[k])
