import urllib.request
import re
import sys

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


def extract_summary_sentence(html: str) -> tuple[str | None, int]:
    """
    Extract the AMS summary sentence:
    'We received X reports about a fireball seen over ...'
    Returns (sentence, report_count)
    """
    # Find the summary paragraph
    m = re.search(r"We received .*? UT\.", html)
    if not m:
        return None, 0

    sentence = m.group(0)

    # Extract the report count from the sentence
    count_match = re.search(r"We received (\d+)", sentence)
    reports = int(count_match.group(1)) if count_match else 0

    return sentence, reports


def classify_priority(reports: int) -> str:
    if reports < 5:
        return "NONE"
    elif reports < 10:
        return "NORMAL"
    else:
        return "HIGH"


def main():
    try:
        browse_html = fetch(BROWSE_URL)
    except Exception as e:
        print("STATUS=ERROR")
        print(f"ERROR={e}")
        sys.exit(0)

    event_url = extract_latest_event_url(browse_html)
    if not event_url:
        print("STATUS=NONE")
        print("REPORTS=0")
        print("SUMMARY=")
        print("URL=")
        sys.exit(0)

    try:
        details_html = fetch(event_url)
    except Exception as e:
        print("STATUS=ERROR")
        print(f"ERROR={e}")
        sys.exit(0)

    summary, reports = extract_summary_sentence(details_html)

    if not summary:
        print("STATUS=NONE")
        print("REPORTS=0")
        print("SUMMARY=")
        print(f"URL={event_url}")
        sys.exit(0)

    status = classify_priority(reports)

    print(f"STATUS={status}")
    print(f"REPORTS={reports}")
    print(f"SUMMARY={summary}")
    print(f"URL={event_url}")


if __name__ == "__main__":
    main()
