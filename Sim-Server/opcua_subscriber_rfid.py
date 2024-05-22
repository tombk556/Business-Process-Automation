from opcua import Client, ua
import time

url = "opc.tcp://192.168.0.1:4840"
node_path = ["2:DeviceSet", "3:PLC_1", "3:DataBlocksGlobal", "3:GDB_OPC-UA", "3:RFID-Reader", "3:Data"]


class SubHandler(object):
    def datachange_notification(self, node, val, data):
        print(f"New Car arrived at visual: {val}")
        print(type(val))
        print(len(val))


if __name__ == '__main__':
    client = Client(url)

    try:
        client.connect()
        print("Client connected to server")

        try:
            # Navigate through the node hierarchy to get the target node
            objects = client.get_objects_node()
            auto_id_node = objects.get_child(node_path)

            handler = SubHandler()
            sub = client.create_subscription(100, handler)

            sub.subscribe_data_change(auto_id_node)
            print("Subscription successful")

            while True:
                time.sleep(1)

        except ua.UaStatusCodeError as e:
            print(f"UaStatusCodeError: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    except ua.UaStatusCodeError as e:
        print(f"Could not connect to the server: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while connecting to the server: {e}")

    finally:
        client.disconnect()
        print("Client disconnected from server")