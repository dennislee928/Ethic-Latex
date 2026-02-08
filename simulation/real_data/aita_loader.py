"""
Reddit r/AmItheAsshole (AITA) loader for empirical moral values.

Structure: (Action/Scenario) -> (YTA/NTA crowd judgment).
Maps voting ratio to V(a) in [-1, 1].
Firecrawl integration for live scraping; stub when unavailable.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import re

_FIRECRAWL_AVAILABLE = False
_FIRECRAWL_V2 = False  # New API: Firecrawl.scrape()
try:
    from firecrawl import Firecrawl
    _FIRECRAWL_AVAILABLE = True
    _FIRECRAWL_V2 = True
except ImportError:
    try:
        from firecrawl import FirecrawlApp
        _FIRECRAWL_AVAILABLE = True
    except ImportError:
        FirecrawlApp = None


def _parse_aita_vote(text: str) -> Optional[float]:
    """
    Parse YTA/NTA ratio from text like "YTA (80%)" or "NTA (70%)".

    Returns V(a) in [-1, 1]: YTA predominant -> negative, NTA -> positive.
    """
    text = (text or "").upper()
    yta_match = re.search(r"YTA\s*\((\d+)%\)", text)
    nta_match = re.search(r"NTA\s*\((\d+)%\)", text)
    if yta_match and nta_match:
        yta_pct = int(yta_match.group(1)) / 100.0
        nta_pct = int(nta_match.group(1)) / 100.0
        total = yta_pct + nta_pct
        if total > 0:
            # V(a) = (NTA - YTA) / (NTA + YTA) in [-1, 1]
            return (nta_pct - yta_pct) / total
    if yta_match:
        return -float(yta_match.group(1)) / 100.0
    if nta_match:
        return float(nta_match.group(1)) / 100.0
    return None


def scrape_aita_firecrawl(
    limit: int = 10,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Scrape r/AmItheAsshole via Firecrawl.

    Supports Firecrawl v2 (Firecrawl.scrape) and legacy FirecrawlApp.scrape_url.
    Returns list of {action_text, verdict, V, score} or stub if unavailable.
    """
    if not _FIRECRAWL_AVAILABLE:
        return _stub_aita_data(limit)
    api_key = api_key or _get_firecrawl_key()
    if not api_key:
        return _stub_aita_data(limit)
    try:
        if _FIRECRAWL_V2:
            from firecrawl import Firecrawl
            app = Firecrawl(api_key=api_key)
            result = app.scrape(
                "https://www.reddit.com/r/AmItheAsshole/top/?t=week",
                formats=["markdown"],
            )
            content = result.get("markdown", result.get("content", "")) if result else ""
        else:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp(api_key=api_key)
            if hasattr(app, "scrape_url"):
                result = app.scrape_url(
                    "https://www.reddit.com/r/AmItheAsshole/top/?t=week",
                )
            else:
                result = app.scrape(
                    "https://www.reddit.com/r/AmItheAsshole/top/?t=week",
                    formats=["markdown"],
                ) if hasattr(app, "scrape") else None
            content = (result.get("markdown", result.get("content", "")) if result else "") if isinstance(result, dict) else ""
        if not content:
            return _stub_aita_data(limit)
        return _parse_aita_content(content, limit)
    except Exception:
        return _stub_aita_data(limit)


def _get_firecrawl_key() -> Optional[str]:
    import os
    return os.environ.get("FIRECRAWL_API_KEY")


def _parse_aita_content(content: str, limit: int) -> List[Dict[str, Any]]:
    """Parse scraped content into action + verdict items."""
    items: List[Dict[str, Any]] = []
    # Heuristic: look for YTA/NTA patterns
    blocks = re.split(r"\n\n+", content)
    for block in blocks[:limit * 3]:
        v = _parse_aita_vote(block)
        if v is not None:
            action = block[:500].strip()
            if action:
                items.append({"action_text": action, "verdict": "YTA" if v < 0 else "NTA", "V": v})
        if len(items) >= limit:
            break
    if not items:
        return _stub_aita_data(limit)
    return items


def _stub_aita_data(limit: int) -> List[Dict[str, Any]]:
    """Stub data when Firecrawl/scraping unavailable."""
    stubs = [
        {"action_text": "Refused to give up seat on bus.", "verdict": "NTA", "V": 0.6},
        {"action_text": "Lied to spouse about finances.", "verdict": "YTA", "V": -0.7},
        {"action_text": "Told friend's secret to others.", "verdict": "YTA", "V": -0.5},
        {"action_text": "Helped stranger with flat tire.", "verdict": "NTA", "V": 0.9},
        {"action_text": "Canceled plans last minute.", "verdict": "NTA", "V": 0.2},
    ]
    return (stubs * ((limit // len(stubs)) + 1))[:limit]


def load_aita_empirical(
    limit: int = 20,
    use_firecrawl: bool = True,
) -> List[Dict[str, Any]]:
    """
    Load AITA-style data for empirical V(a).

    Returns
    -------
    List[Dict]
        Each dict: action_text, verdict, V (moral value in [-1, 1])
    """
    if use_firecrawl and _FIRECRAWL_AVAILABLE and _get_firecrawl_key():
        return scrape_aita_firecrawl(limit=limit)
    return _stub_aita_data(limit)
