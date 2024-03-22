import os
from pynautobot import api

BASE_URL = os.getenv('NAUTOBOT_URL')
TOKEN = os.getenv('TOKEN')


nautobot = api(url=BASE_URL, token=TOKEN)

spine_devices = nautobot.dcim.devices.filter(role='Spine') # return a list of devices with role Spine
spine_devices2 = nautobot.dcim.devices.get(name='Spine-01-2', location='London') # return a single device with name Spine-01-2 and location London

for spine in spine_devices:
   print(spine.name)

print(spine_devices2)
