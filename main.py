import requests
import json
import os

AMS_URL = "https://www.amsmeteors.org/members/api/open_api/get_event_list"

LAST_EVENT_FILE = "last_event.txt"


def get_latest_event_id():
    try:
        response = requests.get(AMS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # AMS returns a list of events; newest is index 0
        if isinstance(data, list) and len(data) > 0:
            return str(data[0].get("id"))
        else:
            return None

    except Exception as e:
        print("DEBUG ERROR in get_latest_event_id:", e)
        return None


def read_last_event():
    if not os.path.exists(LAST_EVENT_FILE):
        return None
    try:
        with open(LAST_EVENT_FILE, "r") as f:
            return f.read().strip()
    except:
        return None


def write_last_event(event_id):
    try:
        with open(LAST_EVENT_FILE, "w") as f:
            f.write(str(event_id))
    except Exception as e:
        print("DEBUG ERROR writing last_event:", e)


def main():
    latest = get_latest_event_id()
    last = read_last_event()

    # Debug prints so GitHub Actions ALWAYS shows something
    print("DEBUG latest =", latest)
    print("DEBUG last   =", last)

    if latest and latest != last:
        print("NEW_EVENT")
        write_last_event(latest)
    else:
        print("NO_EVENT")


if __name__ == "__main__":
    main()
