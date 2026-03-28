import os
import json
from datetime import datetime, timedelta

EVENTS_FILE = "events.json"


def load_events() -> dict:
    if not os.path.exists(EVENTS_FILE):
        return {}
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def is_within_last_24_hours(ts: str | None) -> bool:
    if not ts:
        return False
    try:
        event_time = datetime.fromisoformat(ts)
    except Exception:
        return False
    now = datetime.utcnow()
    return now - timedelta(hours=24) <= event_time <= now


def classify_notable(event: dict) -> list[str]:
    tags: list[str] = []
    reports = event.get("reports", 0)
    summary = (event.get("summary") or "").lower()

    # High witness count
    if reports >= 20:
        tags.append("high witness count")

    # Very rough multi-state heuristic (AMS often mentions states in summary)
    if " over " in summary and " states" in summary:
        tags.append("multi-state")

    # You can add more rules later (brightness, fragmentation, etc.)
    return tags


def build_summary(event_id: str, event: dict) -> str:
    summary = event.get("summary") or ""
    reports = event.get("reports", 0)
    return f"Event {event_id}: {reports} reports — {summary}"


def build_digest(events: list[tuple[str, dict]]) -> str:
    lines: list[str] = []

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines.append("# 🌅 Daily Meteor Activity Report")
    lines.append(f"**Generated:** {now_str}")
    lines.append("")
    lines.append(f"**Total Events (Last 24 Hours):** {len(events)}")
    lines.append("")

    # Notable events
    notable: list[tuple[str, dict, list[str]]] = []
    for eid, ev in events:
        tags = classify_notable(ev)
        if tags:
            notable.append((eid, ev, tags))

    lines.append("## ⭐ Notable Events")
    if not notable:
        lines.append("_No notable events in the last 24 hours._")
    else:
        for eid, ev, tags in notable:
            summary = build_summary(eid, ev)
            tag_str = ", ".join(tags)
            # We don't have the URL stored, but we can reconstruct it:
            url = f"https://fireball.amsmeteors.org/members/imo_view/event/{eid}"
            lines.append(f"- **{summary}**  \n  Tags: {tag_str}  \n  Link: {url}")
    lines.append("")

    # All events
    lines.append("## 🌍 All Events (Past 24 Hours)")
    if not events:
        lines.append("_No events in the last 24 hours._")
    else:
        for eid, ev in events:
            summary = build_summary(eid, ev)
            url = f"https://fireball.amsmeteors.org/members/imo_view/event/{eid}"
            lines.append(f"- {summary}  \n  Link: {url}")
    lines.append("")

    return "\n".join(lines)


def main():
    raw = load_events()

    # raw is {event_id: {summary, reports, timestamp}}
    recent: list[tuple[str, dict]] = []
    for eid, ev in raw.items():
        ts = ev.get("timestamp")
        if is_within_last_24_hours(ts):
            recent.append((eid, ev))

    # Optional: sort by timestamp descending
    def get_ts(ev: dict) -> datetime:
        ts = ev.get("timestamp")
        try:
            return datetime.fromisoformat(ts) if ts else datetime.min
        except Exception:
            return datetime.min

    recent.sort(key=lambda pair: get_ts(pair[1]), reverse=True)

    digest = build_digest(recent)

    # For now, just print it. We'll wire email next.
    print(digest)


if __name__ == "__main__":
    main()
