import urllib.request
import re
import sys
import os
import json
from datetime import datetime, timedelta

BROWSE_URL = "https://fireball.amsmeteors.org/members/imo_view/browse_events"
EVENTS_FILE = "events.json"


# -----------------------------
# Fetch URL
# -----------------------------
def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


# -----------------------------
# Extract top N event URLs
# -----------------------------
def extract_latest_event_urls(html: str, count=5) -> list[str]:
    matches = re.findall(r'href="(/members/imo_view/event/\d+[^"]*)"', html)
    return ["https://fireball.amsmeteors.org" + m for m in matches[:count]]


# -----------------------------
# Extract event ID
# -----------------------------
def extract_event_id(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r'/event/\d+/(\d+)', url)
    if m:
        return m.group(1)
    nums = re.findall(r'\d+', url)
    return nums[-1] if nums else None


# -----------------------------
# Extract summary, reports, timestamp
# -----------------------------
def extract_event_details(html: str):
    m = re.search(r"We received[\s\S]*?UT\.", html)
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


# -----------------------------
# Priority classification
# -----------------------------
def classify_priority(reports: int) -> str:
    if reports <= 9:
        return "LOW"
    elif reports <= 19:
        return "REGULAR"
    else:
        return "HIGH"


# -----------------------------
# Load stored events.json
# -----------------------------
def load_events():
    if not os.path.exists(EVENTS_FILE):
        return {}
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# -----------------------------
# Save updated events.json
# -----------------------------
def save_events(data):
    try:
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# -----------------------------
# Main
# -----------------------------
def main():
    # Fetch the AMS browse page
    try:
        browse_html = fetch(BROWSE_URL)
    except Exception as e:
        print(f"ERROR={e}")
        sys.exit(0)

    # Extract latest event URLs
    event_urls = extract_latest_event_urls(browse_html, count=5)
    if not event_urls:
        print("EVENT_COUNT=0")
        sys.exit(0)

    stored = load_events()
    now = datetime.utcnow()
    lookback_start = now - timedelta(hours=8)

    output_lines = []
    updated_events = {}

    index = 1

    for url in event_urls:
        try:
            html = fetch(url)
        except Exception:
            continue

        summary, reports, event_time = extract_event_details(html)
        event_id = extract_event_id(url)

        if not event_id or not summary:
            continue

        # Determine if inside 8-hour window
        inside_window = event_time >= lookback_start if event_time else False

        # Compare with stored data
        old = stored.get(event_id, {})
        old_summary = old.get("summary")
        old_reports = old.get("reports")

        new_event = event_id not in stored
        summary_changed = (summary != old_summary)
        reports_changed = (reports != old_reports)

        unchanged = not (new_event or summary_changed or reports_changed)

        # -----------------------------
        # Explicit NEW vs UPDATED logic
        # -----------------------------
        if new_event:
            event_type = "NEW"
        elif summary_changed or reports_changed:
            event_type = "UPDATED"
        else:
            event_type = "NONE"

        status = classify_priority(reports)

        # Build output for GitHub Actions
        prefix = f"EVENT_{index}"
        output_lines.append(f"{prefix}_ID={event_id}")
        output_lines.append(f"{prefix}_STATUS={status}")
        output_lines.append(f"{prefix}_REPORTS={reports}")
        output_lines.append(f"{prefix}_SUMMARY={summary}")
        output_lines.append(f"{prefix}_UNCHANGED={'YES' if unchanged else 'NO'}")
        output_lines.append(f"{prefix}_EVENT_TYPE={event_type}")
        output_lines.append(f"{prefix}_INSIDE_WINDOW={'YES' if inside_window else 'NO'}")
        output_lines.append(f"{prefix}_URL={url}")

        # Save updated event info
        updated_events[event_id] = {
            "summary": summary,
            "reports": reports,
            "timestamp": event_time.isoformat() if event_time else None
        }

        index += 1

    # Print all event outputs
    print(f"EVENT_COUNT={index - 1}")
    for line in output_lines:
        print(line)

    # Save updated memory
    save_events(updated_events)


if __name__ == "__main__":
    main()
