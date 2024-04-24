from opcua import Client, ua

class OPCUASubscriber:
    def __init__(self, server_url, node_id):
        self.server_url = server_url
        self.node_id = node_id
        self.client = Client(self.server_url)
        self.last_value = False

    class SubHandler(object):
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def datachange_notification(self, node, val, data):
            print(f"Data change detected. Node: {node}, New Value: {val}")
            if not self.outer.last_value and val:
                print("Value changed from False to True!")
            self.outer.last_value = val

    def connect(self):
        self.client.connect()
        print("Client connected to server.")

    def subscribe_to_changes(self):
        handler = self.SubHandler(self)
        sub = self.client.create_subscription(100, handler)
        node = self.client.get_node(self.node_id)
        sub.subscribe_data_change(node)
        print(f"Subscribed to node: {node}. Listening for changes...")

    def run(self):
        try:
            self.connect()
            self.subscribe_to_changes()
            while True:
                pass
        except KeyboardInterrupt:
            print("Received interrupt signal, stopping subscription")
        finally:
            self.disconnect()

    def disconnect(self):
        self.client.disconnect()
        print("Client disconnected")

if __name__ == "__main__":
    server_url = "opc.tcp://uademo.prosysopc.com:53530/OPCUA/SimulationServer"
    node_id = "ns=6;s=MySwitch" 
    subscriber = OPCUASubscriber(server_url, node_id)
    subscriber.run()
