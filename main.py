import urllib.request
import re
import sys
import os
from datetime import datetime, timedelta

BROWSE_URL = "https://fireball.amsmeteors.org/members/imo_view/browse_events"
LAST_SUMMARY_FILE = "last_summary.txt"
LAST_EVENT_FILE = "last_event_url.txt"


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_latest_event_url(html: str) -> str | None:
    m = re.search(r'href="(/members/imo_view/event/\d+[^"]*)"', html)
    if not m:
        return None
    return "https://fireball.amsmeteors.org" + m.group(1)


def extract_event_id(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r'/event/\d+/(\d+)', url)
    if m:
        return m.group(1)
    # fallback: extract last number anywhere
    m = re.findall(r'\d+', url)
    return m[-1] if m else None


def extract_summary_sentence(html: str) -> tuple[str | None, int, datetime | None]:
    m = re.search(r"We received .*? UT\.", html)
    if not m:
        return None, 0, None

    sentence = m.group(0)

    count_match = re.search(r"We received (\d+)", sentence)
    reports = int(count_match.group(1)) if count_match else 0

    t = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UT", html)
    if t:
        try:
            event_time = datetime.strptime(t.group(1), "%Y-%m-%d %H:%M:%S")
        except Exception:
            event_time = None
    else:
        event_time = None

    return sentence, reports, event_time


def classify_priority(reports: int) -> str:
    if reports <= 9:
        return "LOW"
    elif reports <= 19:
        return "REGULAR"
    else:
        return "HIGH"


def load_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def save_file(path: str, text: str):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass


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
        print("UNCHANGED=YES")
        print("EVENT_TYPE=NONE")
        print("INSIDE_WINDOW=NO")
        print("URL=")
        sys.exit(0)

    try:
        details_html = fetch(event_url)
    except Exception as e:
        print("STATUS=ERROR")
        print(f"ERROR={e}")
        sys.exit(0)

    summary, reports, event_time = extract_summary_sentence(details_html)

    if not summary:
        print("STATUS=NONE")
        print("REPORTS=0")
        print("SUMMARY=")
        print("UNCHANGED=YES")
        print("EVENT_TYPE=NONE")
        print("INSIDE_WINDOW=NO")
        print(f"URL={event_url}")
        sys.exit(0)

    now = datetime.utcnow()
    lookback_start = now - timedelta(hours=8)
    inside_window = event_time >= lookback_start if event_time else False

    last_summary = load_file(LAST_SUMMARY_FILE)
    last_event_raw = load_file(LAST_EVENT_FILE)

    new_id = extract_event_id(event_url)
    old_id = extract_event_id(last_event_raw)

    new_event = (new_id != old_id)
    unchanged = (summary == last_summary)

    if new_event:
        event_type = "CONFIRMED"
    else:
        event_type = "UPDATED" if not unchanged else "NONE"

    if new_event or not unchanged:
        save_file(LAST_SUMMARY_FILE, summary)
        save_file(LAST_EVENT_FILE, event_url)

    status = classify_priority(reports)

    print(f"STATUS={status}")
    print(f"REPORTS={reports}")
    print(f"SUMMARY={summary}")
    print(f"UNCHANGED={'YES' if unchanged else 'NO'}")
    print(f"EVENT_TYPE={event_type}")
    print(f"INSIDE_WINDOW={'YES' if inside_window else 'NO'}")
    print(f"URL={event_url}")


if __name__ == "__main__":
    main()
