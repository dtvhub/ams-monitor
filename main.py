import requests
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

        return None

    except Exception as e:
        print(f"DEBUG_ERROR {e}")
        return None


def read_last_event():
    if not os.path.exists(LAST_EVENT_FILE):
        return None
    try:
        with open(LAST_EVENT_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"DEBUG_READ_ERROR {e}")
        return None


def write_last_event(event_id):
    try:
        with open(LAST_EVENT_FILE, "w") as f:
            f.write(str(event_id))
    except Exception as e:
        print(f"DEBUG_WRITE_ERROR {e}")


def main():
    latest = get_latest_event_id()
    last = read_last_event()

    # Debug output (safe for GitHub Actions)
    print(f"DEBUG_LATEST {latest}")
    print(f"DEBUG_LAST {last}")

    if latest and latest != last:
        print("NEW_EVENT")
        write_last_event(latest)
    else:
        print("NO_EVENT")


if __name__ == "__main__":
    main()
