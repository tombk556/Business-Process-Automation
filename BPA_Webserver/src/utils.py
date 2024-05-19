from opcua import Client
import requests
import time
import sys
sys.path.append('../')
from config import settings


opcua_url = settings.opcua_url
trigger_url = settings.aas_url
latest_auto_id = None

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        global latest_auto_id
        latest_auto_id = val
        print(f"New data change event: {val}")
        trigger_action_based_on_auto_id(val)

def trigger_action_based_on_auto_id(auto_id):
    try:
        response = requests.get(trigger_url, params={'auto_id': auto_id})
        if response.status_code == 200:
            href = search_id_short_and_href(response.json(), auto_id)
            if href:
                print(href)
            else: 
                print(f"Failed to find href for Auto ID: {auto_id}")
        else:
            print(f"Failed to trigger action for Auto ID: {auto_id}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error triggering action for Auto ID: {auto_id}, error: {e}")

def opcua_subscriber():
    client = Client(opcua_url)
    
    try:
        client.connect()
        print("Connected to OPC UA server")
        
        # Get the objects node
        objects = client.get_objects_node()
        
        # Get the AutoID variable node
        auto_id_obj = objects.get_child(["2:AutoID"])
        auto_id_node = auto_id_obj.get_child(["2:AutoID"])
        
        # Create a subscription handler
        handler = SubHandler()
        sub = client.create_subscription(100, handler)
        
        # Subscribe to the AutoID variable node
        sub.subscribe_data_change(auto_id_node)
        
        # Keep the client running to receive data change events
        while True:
            time.sleep(1)
    
    finally:
        client.disconnect()
        print("Disconnected from OPC UA server")

def search_id_short_and_href(data: dict, target_id_short: str) -> str:
    if isinstance(data, dict):
        if data.get("idShort") == target_id_short:
            endpoints = data.get("endpoints")
            if endpoints:
                href = endpoints[0].get("protocolInformation", {}).get("href")
                return data["idShort"], href
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                result = search_id_short_and_href(value, target_id_short)
                if result:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = search_id_short_and_href(item, target_id_short)
            if result:
                return result
    return None