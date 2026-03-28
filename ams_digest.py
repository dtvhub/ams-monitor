import os
import datetime as dt
import requests

AMS_BASE_URL = "https://example.com/ams/api"  # placeholder

def fetch_events():
    # TODO: replace with the real AMS endpoint you already use
    resp = requests.get(AMS_BASE_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()

def is_within_last_24_hours(event_time_utc: dt.datetime) -> bool:
    now = dt.datetime.utcnow()
    return now - dt.timedelta(hours=24) <= event_time_utc <= now

def parse_event_time(event) -> dt.datetime:
    # TODO: adapt to AMS time format
    # Example if it's ISO:
    return dt.datetime.fromisoformat(event["time_utc"].replace("Z", "+00:00")).replace(tzinfo=None)

def classify_notable(event) -> list[str]:
    tags = []
    # TODO: adapt keys to your actual AMS JSON
    if event.get("multi_state"):
        tags.append("multi-state")
    if event.get("report_count", 0) >= 20:
        tags.append("high witness count")
    if event.get("has_trajectory"):
        tags.append("trajectory")
    if event.get("daytime"):
        tags.append("daytime")
    if event.get("meteorite_potential"):
        tags.append("meteorite potential")
    return tags

def build_summary(event) -> str:
    # TODO: adapt keys
    eid = event.get("id")
    loc = event.get("location", "Unknown location")
    reports = event.get("report_count", 0)
    return f"Event {eid}: {reports} reports near {loc}"

def build_digest(events: list[dict]) -> str:
    lines = []
    now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"# 🌅 Daily Meteor Activity Report")
    lines.append(f"**Generated:** {now}")
    lines.append("")
    lines.append(f"**Total Events (Last 24 Hours):** {len(events)}")
    lines.append("")
    
    # Notable events
    notable = []
    for e in events:
        tags = classify_notable(e)
        if tags:
            notable.append((e, tags))

    lines.append("## ⭐ Notable Events")
    if not notable:
        lines.append("_No notable events in the last 24 hours._")
    else:
        for e, tags in notable:
            eid = e.get("id")
            url = e.get("url", "")
            summary = build_summary(e)
            tag_str = ", ".join(tags)
            lines.append(f"- **{summary}**  \n  Tags: {tag_str}  \n  Link: {url}")
    lines.append("")

    # All events
    lines.append("## 🌍 All Events (Past 24 Hours)")
    if not events:
        lines.append("_No events in the last 24 hours._")
    else:
        for e in events:
            summary = build_summary(e)
            url = e.get("url", "")
            lines.append(f"- {summary}  \n  Link: {url}")
    lines.append("")

    return "\n".join(lines)

def send_email(to_address: str, subject: str, body: str):
    # IMPORTANT: reuse whatever email-sending mechanism you already use
    # for AMS alerts (SMTP, API, etc.).
    # Here we just print as a placeholder.
    print("=== EMAIL TO:", to_address, "===")
    print("SUBJECT:", subject)
    print(body)

def main():
    to_address = os.environ.get("AMS_MONITOR_ADDRESS")
    if not to_address:
        raise RuntimeError("AMS_MONITOR_ADDRESS not set")

    raw_events = fetch_events()

    # TODO: adapt to actual structure (e.g., raw_events["events"])
    events = []
    for e in raw_events:
        t = parse_event_time(e)
        if is_within_last_24_hours(t):
            events.append(e)

    # sort by time if you have it
    # events.sort(key=lambda e: parse_event_time(e))

    digest = build_digest(events)
    subject = "Daily AMS Meteor Digest"
    send_email(to_address, subject, digest)

if __name__ == "__main__":
    main()
