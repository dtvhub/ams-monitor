import requests
import os
from bs4 import BeautifulSoup

AMS_URL = "https://fireball.amsmeteors.org/members/imo_view/browse_events"
LAST_EVENT_FILE = "last_event.txt"


def get_latest_event_id():
    try:
        response = requests.get(AMS_URL, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # The first event row is always the newest
        first_row = soup.select_one("table tbody tr")

        if not first_row:
            print("DEBUG_ERROR No table rows found")
            return None

        # Event ID is in the first <td>
        event_id_cell = first_row.find("td")
        if not event_id_cell:
            print("DEBUG_ERROR No event ID cell found")
            return None

        event_id = event_id_cell.text.strip()
        return event_id

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

    print(f"DEBUG_LATEST {latest}")
    print(f"DEBUG_LAST {last}")

    if latest and latest != last:
        print("NEW_EVENT")
        write_last_event(latest)
    else:
        print("NO_EVENT")


if __name__ == "__main__":
    main()
