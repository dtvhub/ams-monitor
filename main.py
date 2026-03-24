import requests
import os

AMS_URL = "https://fireball.amsmeteors.org/members/imo_view/browse_events"
LAST_ID_FILE = "ams_last_id.txt"

def fetch_latest_event_id():
    response = requests.get(AMS_URL)
    if response.status_code != 200:
        raise Exception("Failed to fetch AMS page")
    html = response.text
    marker = "/members/imo_view/event/"
    start = html.find(marker)
    if start == -1:
        raise Exception("No event ID found")
    end = html.find('"', start)
    event_url = html[start:end]
    event_id = event_url.split("/")[-1]
    return event_id

def read_last_id():
    if not os.path.exists(LAST_ID_FILE):
        return None
    with open(LAST_ID_FILE, "r") as f:
        return f.read().strip()

def write_last_id(event_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(event_id)

def trigger_ifttt(event_id):
    key = os.getenv("IFTTT_KEY")
    if not key:
        raise Exception("Missing IFTTT key")
    url = f"https://maker.ifttt.com/trigger/ams_event/with/key/{key}"
    data = {"value1": f"New AMS event: {event_id}"}
    requests.post(url, json=data)

def main():
    latest_id = fetch_latest_event_id()
    last_id = read_last_id()
    if latest_id != last_id:
        print(f"New event detected: {latest_id}")
        trigger_ifttt(latest_id)
        write_last_id(latest_id)
    else:
        print("No new event.")

if __name__ == "__main__":
    main()