import os
import requests

BASE_URL = os.getenv('NAUTOBOT_URL')
TOKEN = os.getenv('TOKEN')
LOCATIONS_ENDPOINT = 'api/dcim/locations/'


HEADERS = {
   'Authorization': f'Token {TOKEN}',
   'Content-Type': 'application/json',
   'Accept': 'application/json',
}


def display_locations(locations_url):
   response = requests.get(locations_url, headers=HEADERS)
   if response.status_code == 200:
       locations = response.json()
       for location in locations['results']:
           print(f"Name: {location['name']}")
   else:
       print(f"Failed to fetch locations: {response.status_code}")


locations_url = f"{BASE_URL}{LOCATIONS_ENDPOINT}"
display_locations(locations_url)
