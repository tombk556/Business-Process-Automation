from opcua import Client
import time
from config import settings

latest_auto_id = None

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        global latest_auto_id
        latest_auto_id = val
        print(f"New data change event: {val}")

def opcua_subscriber(opcua_url: str = settings.opcua_url):
    client = Client(opcua_url)
    
    try:
        client.connect()
        print("Connected to OPC UA server")
        
        objects = client.get_objects_node()
        
        auto_id_obj = objects.get_child(["2:AutoID"])
        auto_id_node = auto_id_obj.get_child(["2:AutoID"])
        
        handler = SubHandler()
        sub = client.create_subscription(100, handler)
        
        sub.subscribe_data_change(auto_id_node)
        
        while True:
            time.sleep(1)
    
    finally:
        client.disconnect()
        print("Disconnected from OPC UA server")