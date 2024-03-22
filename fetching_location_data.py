import os
import requests
from pprint import pprint

BASE_URL = os.getenv('NAUTOBOT_URL')
TOKEN = os.getenv('TOKEN')
LOCATIONS_ENDPOINT = 'api/dcim/locations/'


HEADERS = {
   'Authorization': f'Token {TOKEN}',
   'Content-Type': 'application/json',
   'Accept': 'application/json',
}

full_url = f"{BASE_URL}{LOCATIONS_ENDPOINT}"

response = requests.get(full_url, headers=HEADERS)

if response.status_code == 200:
   locations = response.json()
   pprint(locations)
   for location in locations['results']:
       print(f"Name: {location['name']}")
else:
   print(f"Failed to fetch locations: {response.status_code}")
