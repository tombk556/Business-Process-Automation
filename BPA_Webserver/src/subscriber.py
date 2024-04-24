from opcua import Client, ua

class SubHandler(object):
    """
    Subscription Handler class to handle data changes from the OPC-UA server.
    """
    def __init__(self, client):
        self.client = client
        self.last_value = False  # Initialize with the value being False

    def datachange_notification(self, node, val, data):
        print(f"Data change detected. Node: {node}, New Value: {val}")
        if not self.last_value and val:  # Checks if the last value was False and the new value is True
            print("Value changed from False to True!")
        self.last_value = val  # Update last_value with the new value

def main():
    # Connect to the OPC UA server
    client = Client("opc.tcp://uademo.prosysopc.com:53530/OPCUA/SimulationServer")  # Replace the URL with your server URL
    try:
        client.connect()
        print("Client connected")

        # Create a subscription and pass the client to the handler
        sub = client.create_subscription(100, SubHandler(client))

        # Subscribe to data changes for a specific Boolean node
        node = client.get_node("ns=6;s=MySwitch")  # Replace with your actual NodeId
        sub.subscribe_data_change(node)

        print("Subscribed to data changes for node:", node)

        # Let the subscription run for a while
        try:
            print("Subscription running... Press Ctrl+C to exit")
            while True:
                pass
        except KeyboardInterrupt:
            print("Received interrupt signal, stopping subscription")

    finally:
        # Disconnect the client
        client.disconnect()
        print("Client disconnected")

if __name__ == "__main__":
    main()
