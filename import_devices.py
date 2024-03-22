import pynautobot
from ipaddress import ip_network, ip_address
import os

# Configuration

NAUTOBOT_URL = os.environ.get("NAUTOBOT_URL")
TOKEN = os.environ.get("TOKEN")


# Initialize Pynautobot API
api = pynautobot.api(url=NAUTOBOT_URL, token=TOKEN)
api.http_session.verify = False  # Disable for development or with trusted SSL certificates

# Functions

def create_spine_devices(location, rack):
   current_rack_name_prefix = rack.name.split("-")[1]
   device_role = api.extras.roles.get(name="Spine")
   device_type = api.dcim.device_types.get(model="QFX5120-48Y-AFO2")
  
   for i in range(0, 2):
       rack_position = 42 - i
       device_name = f"Spine-{current_rack_name_prefix}-{i+1}"
       create_device(device_name, device_role.id, device_type.id, location.id, rack.id, position=rack_position, face="front")

def create_leaf_devices(location, rack):
   current_rack_name_prefix = rack.name.split("-")[1]
   device_role = api.extras.roles.get(name="Leaf")
   device_type = api.dcim.device_types.get(model="QFX5120-48Y-AFO2")
  
   for i in range(0, 2):
       rack_position = 42 - i
       device_name = f"Leaf-{current_rack_name_prefix}-{i+1}"
       create_device(device_name, device_role.id, device_type.id, location.id, rack.id, position=rack_position, face="front")

def create_device( name, device_role, device_type, location, rack, position, face):
   if api.dcim.devices.get(name=name,location=location,rack=rack):
       print(f"Device {name} already exists")
   else:
       print(f"Creating device {name}")
       device = api.dcim.devices.create(
           name=name,
           role=device_role,
           device_type=device_type,
           location=location,
           rack=rack,
           status='Active',
           position=position,
           face=face
       )
       return device

def create_ip_addresses(address, tag):
   if api.ipam.ip_addresses.get(address=address):
       print(f"IP address {address} already exists")
   else:
       print(f"Creating IP address {address}")
       ip = api.ipam.ip_addresses.create(
           address=address,
           namespace="Global",
           status='Active',
           tags = [tag],
       )
       return ip

def create_prefix_tags(tag):
   if api.extras.tags.get(name=tag):
       print(f"Tag {tag} already exists")
   else:
       print(f"Creating tag {tag}")
       tag = api.extras.tags.create(
           name=tag,
           content_types=["ipam.ipaddress","dcim.location","ipam.prefix"],
       )
       return tag
  
def assign_ip_to_interface(interface, ip):
   if api.ipam.ip_address_to_interface.get(ip_address=ip['id']):
       print(f"IP address with ID {ip['id']} already assigned to interface")
   else:
       print(f"Assigning IP address to interface")
       ip = api.ipam.ip_address_to_interface.create(
           ip_address=ip,
           interface=interface,
           is_primary=True,
       )
       return ip

def assign_primary_ip_to_device(device, ip):
   if device.primary_ip4:
       print(f"Device {device.name} already has a primary IP address")
   else:
       print(f"Assigning IP address to device")
       ip = api.dcim.devices.update(
           id = device.id,
           data = {"primary_ip4": ip['id']}
       )
       return ip


# Main script

print("Creating datacenter fabric devices")

nautobot_locations = api.dcim.locations.all()

for location in nautobot_locations:

   # Adding tags based on location name
   tag = location.name
   create_prefix_tags(tag)

for location in nautobot_locations:
  
   # Creatig devices for each rack
   racks = api.dcim.racks.filter(location=location.id)
   for rack in racks:
       if "Rack-01" in rack.name:
           create_spine_devices(location, rack)
       else:
           create_leaf_devices(location, rack)

   # Creating IP addresses for the devices
          
   devices = api.dcim.devices.filter(location=location.id)
   count = 0
   for device in devices:
       count += 1
       prefix = api.ipam.prefixes.get(location=location.id)
       subnet = ip_network(prefix.prefix)
       prefix_lenght = subnet.prefixlen
       ip = ip_address(subnet.network_address + count)
       tag_id= api.extras.tags.get(name=location.name).id
       create_ip_addresses(str(ip) + "/" + str(prefix_lenght), tag_id)
  
  # Assigning IP addresses to devices
  
nautobot_locations = api.dcim.locations.all()

for location in nautobot_locations:
   devices = api.dcim.devices.filter(location=location.id)
   ip_address_id_object_list = api.ipam.ip_addresses.filter(tags=location.name)
   ip_address_id_list = [ip.id for ip in ip_address_id_object_list]

   for device in devices:
       interface_id = api.dcim.interfaces.filter(device=device.name, name="fxp0",location=location.id)[0].id
       ip_id = ip_address_id_list[0]
       ip_address_id_list.pop(0)
       interface_dict =  {
           "id": interface_id,
           "object_type": "dcim.interface",
           }
       ip_dict = {
           "id": ip_id,
           "object_type": "ipam.ipaddress",
           }
       assign_ip_to_interface(interface_dict, ip_dict)
       assign_primary_ip_to_device(device, ip_dict)
  


print("Datacenter fabric devices created successfully")
