from opcua import Client
import time

url = "opc.tcp://localhost:4840"
node = "2:AutoID"

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        print(f"New Car arrived at visual: {val}")

if __name__ == '__main__':
    client = Client(url)

    try:
        client.connect()
        print("Client connected to server")

        objects = client.get_objects_node()
        auto_id_obj = objects.get_child([node])
        auto_id_node = auto_id_obj.get_child([node])

        handler = SubHandler()
        sub = client.create_subscription(100, handler)

        sub.subscribe_data_change(auto_id_node)

        while True:
            time.sleep(1)

    finally:
        client.disconnect()
        print("Client disconnected from server")
