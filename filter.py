import re
import requests
from icalendar import Calendar

SOURCE_ICS_URL = "https://starsaas.deakin.edu.au/even/rest/calendar/ical/74aba146-7b13-4598-9e87-5ecb4d1d3ea4"
OUTPUT_FILE = "filtered_deakin_calendar.ics"

KEEP_TYPES = ["Lab", "Ast"]
HIDE_TYPES = ["Wrk", "Lec"]

response = requests.get(SOURCE_ICS_URL)
response.raise_for_status()

calendar = Calendar.from_ical(response.content)

new_calendar = Calendar()
new_calendar.add("prodid", "-//Filtered Deakin Calendar//")
new_calendar.add("version", "2.0")

for component in calendar.walk():
    if component.name != "VEVENT":
        continue

    summary = str(component.get("summary", ""))
    description = str(component.get("description", ""))
    location = str(component.get("location", ""))

    full_text = f"{summary} {description}"

    if any(hidden in full_text for hidden in HIDE_TYPES):
        continue

    if not any(keep in full_text for keep in KEEP_TYPES):
        continue

    unit_match = re.search(r"(SLE\d{3})", full_text)
    unit_code = unit_match.group(1) if unit_match else "Class"

    # Shorten known unit names
    subject_name = ""
    if "Synthetic and medicinal" in full_text or "Sythetic and medicinal" in full_text:
        subject_name = "Synthetic"

    # Get room, e.g. LC4.105
    room_match = re.search(r"\b[A-Z]{1,4}\d?\.\d{3}\b", full_text)
    room = room_match.group(0) if room_match else location

    new_title = f"{unit_code} {subject_name} {room}".strip()

    component["summary"] = new_title
    new_calendar.add_component(component)

with open(OUTPUT_FILE, "wb") as f:
    f.write(new_calendar.to_ical())

print(f"Saved filtered calendar as {OUTPUT_FILE}")
