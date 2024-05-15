from flask import Flask, jsonify
from opcua import Client, ua
import threading
import time
import requests

app = Flask(__name__)

# OPC UA server endpoint URL
opcua_url = "opc.tcp://localhost:4840"
latest_auto_id = None

# URL of the endpoint to trigger with the Auto ID
trigger_url = "http://141.56.180.118:8080/shell-descriptors"  # Replace with the actual URL

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
            print(f"Successfully triggered action for Auto ID: {auto_id}")
            print(response.json())
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

@app.route('/latest_auto_id', methods=['GET'])
def get_latest_auto_id():
    global latest_auto_id
    if latest_auto_id is not None:
        return jsonify({"auto_id": latest_auto_id})
    else:
        return jsonify({"message": "No Auto ID received yet"}), 404

if __name__ == '__main__':
    # Run the OPC UA subscriber in a separate thread
    subscriber_thread = threading.Thread(target=opcua_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=True)
