from opcua import Client, ua
import time
import threading

url = "opc.tcp://192.168.0.1:4840"
node_path = ["2:DeviceSet", "3:PLC_1", "3:DataBlocksGlobal", "3:GDB_OPC-UA", "3:RFID-Reader", "3:StartScan"]


def input_listener(client):
    while True:
        input("Drücken Sie die Eingabetaste, um StartScan auf True zu setzen...\n")
        set_start_scan(client)
        time.sleep(2)



def set_start_scan(client):
    try:
        objects = client.get_objects_node()
        start_scan_node = objects.get_child(node_path)

        # Den alten Wert abrufen und ausdrucken
        old_value = start_scan_node.get_value()
        print(f"Alter Wert für Knoten {'/'.join(node_path)}: {old_value}")

        val = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
        start_scan_node.set_value(val)
        val = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
        start_scan_node.set_value(val)

    except ua.UaStatusCodeError as e:
        print(f"UaStatusCodeError: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


if __name__ == '__main__':
    client = Client(url)

    try:
        client.connect()
        print("Client mit Server verbunden")

        input_thread = threading.Thread(target=input_listener, args=(client,))
        input_thread.daemon = True
        input_thread.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Client wird gestoppt...")
    except ua.UaStatusCodeError as e:
        print(f"Verbindung zum Server konnte nicht hergestellt werden: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist bei der Verbindung zum Server aufgetreten: {e}")
    finally:
        client.disconnect()
        print("Client vom Server getrennt")