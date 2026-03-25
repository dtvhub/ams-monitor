import urllib.request
import re
import sys
from datetime import datetime, timezone

BROWSE_URL = "https://fireball.amsmeteors.org/members/imo_view/browse_events"


def fetch(url: str) -> str:
    """Fetch HTML from a URL."""
    with urllib.request.urlopen(url, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_latest_event_url(html: str) -> str | None:
    """Extract the first (newest) event URL from the browse page."""
    m = re.search(r'href="(/members/imo_view/event/\d+[^"]*)"', html)
    if not m:
        return None
    return "https://fireball.amsmeteors.org" + m.group(1)


def extract_summary_sentence(html: str) -> tuple[str | None, int, str | None]:
    """
    Extract the AMS summary sentence:
    'We received X reports about a fireball seen over ... UT.'
    Returns (sentence, report_count, timestamp_string)
    """
    m = re.search(r"We received .*? UT\.", html)
    if not m:
        return None, 0, None

    sentence = m.group(0)

    # Extract report count
    count_match = re.search(r"We received (\d+)", sentence)
