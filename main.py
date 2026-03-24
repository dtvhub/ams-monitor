import requests
import os
import re

AMS_URL = "https://www.amsmeteors.org/members/imo_view/browse_events"

def get_latest_event_id():
    r = requests.get(AMS_URL)
    r.raise_for_status()
    text = r.text

    # AMS event IDs look like: 20260324-123456
    match = re.search(r"\d{8}-\d{6}", text)
    if match:
        return match.group(0)
    return None

def read_last_event():
    if not os.path.exists("last_event.txt"):
        return None
    with open("last_event.txt", "r") as f:
        return f.read().strip()

def write_last_event(event_id):
    with open("last_event.txt", "w") as f:
        f.write(event_id)

latest = get_latest_event_id()
last = read_last_event()

if latest and latest != last:
    print("NEW_EVENT")
    write_last_event(latest)
else:
    print("NO_EVENT")