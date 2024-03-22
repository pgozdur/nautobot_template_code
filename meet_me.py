import os
import requests


BASE_URL = os.getenv('NAUTOBOT_URL')
TOKEN = os.getenv('TOKEN')

HEADERS = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def fetch_location_id(location_name, locations_url):
    response = requests.get(locations_url, headers=HEADERS)
    if response.status_code == 200:
        locations = response.json()
        for location in locations['results']:
            if location['name'].lower() == location_name.lower():
                return location['id']
    else:
        print(f"Failed to fetch locations: {response.status_code}")
    return None


LOCATIONS_ENDPOINT = 'api/dcim/locations/'
locations_url = f"{BASE_URL}{LOCATIONS_ENDPOINT}"
london_location_id = fetch_location_id("London", locations_url)


new_rack_payload = {
   "name": "meet-me-room",
   "location": london_location_id,
   "status": "Active",
   # Add other necessary rack properties here
}

RACKS_ENDPOINT = 'api/dcim/racks/'
racks_url = f"{BASE_URL}{RACKS_ENDPOINT}"

response = requests.post(racks_url, headers=HEADERS, json=new_rack_payload)

if response.status_code == 201:
    print("New rack added successfully.")
else:
    print(f"Failed to add the new rack: {response.status_code}")




