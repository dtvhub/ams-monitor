import urllib.request
import re
import sys

AMS_EVENTS_URL = "https://fireball.amsmeteors.org/members/imo_view/browse_events"

# Valid US state abbreviations
US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY"
}

# Canadian provinces/territories
CA_PROVINCES = {
    "AB","BC","MB","NB","NL","NS","NT","NU","ON","PE","QC","SK","YT"
}

# Australian states/territories
AU_STATES = {
    "NSW","QLD","SA","TAS","VIC","WA","ACT","NT"
}

# UK subdivisions (common ones AMS might show)
UK_REGIONS = {
    "ENG","SCT","WLS","NIR"
}

# ISO‑3166 country codes (common)
COUNTRIES = {
    "US","CA","MX","UK","AU","FR","DE","ES","IT","BR","JP","CN","RU","IN","NZ",
    "SE","NO","FI","DK","PL","PT","GR","CH","AT","BE","NL","CZ","SK","HU","RO",
    "BG","TR","ZA","AR","CL","CO","PE"
}

# Combine all valid tokens
VALID_CODES = US_STATES | CA_PROVINCES | AU_STATES | UK_REGIONS | COUNTRIES


def fetch_html(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_first_event(html: str):
    # Find first event URL
    m = re.search(r'href="(/members/imo_view/event/\d+[^"]*)"', html)
    if not m:
        return None

    event_path = m.group(1)
    event_url = "https://fireball.amsmeteors.org" + event_path

    # Take a window around the match to search for reports and locations
    start = max(0, m.start() - 800)
    end = min(len(html), m.end() + 800)
    snippet = html[start:end]

    # Reports (e.g., "7 reports")
    reports_match = re.search(r'(\d+)\s+reports', snippet, re.IGNORECASE)
    reports = int(reports_match.group(1)) if reports_match else 0

    # Extract all uppercase tokens (2–3 letters)
    raw_tokens = re.findall(r'\b[A-Z]{2,3}\b', snippet)

    # Filter to valid global codes, dedupe, preserve order
    seen = set()
    locations = []
    for token in raw_tokens:
        if token in VALID_CODES and token not in seen:
            seen.add(token)
            locations.append(token)

    location_str = ", ".join(locations) if locations else "Unknown location"

    return {
        "url": event_url,
        "reports": reports,
        "locations": location_str,
    }


def classify_priority(reports: int) -> str:
    if reports < 5:
        return "NONE"
    elif reports < 10:
        return "NORMAL"
    else:
        return "HIGH"


def main():
    try:
        html = fetch_html(AMS_EVENTS_URL)
    except Exception as e:
        print("STATUS=ERROR")
        print(f"ERROR={e}")
        sys.exit(0)

    event = extract_first_event(html)
    if not event:
        print("STATUS=NONE")
        print("REPORTS=0")
        print("LOCATIONS=Unknown location")
        print("URL=")
        sys.exit(0)

    status = classify_priority(event["reports"])

    print(f"STATUS={status}")
    print(f"REPORTS={event['reports']}")
    print(f"LOCATIONS={event['locations']}")
    print(f"URL={event['url']}")


if __name__ == "__main__":
    main()
