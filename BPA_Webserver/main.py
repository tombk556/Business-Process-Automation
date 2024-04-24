from opcua import Client
import time


def opcua_server():
    url = "opc.tcp://uademo.prosysopc.com:53530/OPCUA/SimulationServer"
    client = Client(url)
    return client


def get_node_data(node_id: str, client: Client = opcua_server()):
    try:
        client.connect()
        node = client.get_node(node_id)
        return node.get_data_value()
    except Exception as e:
        print("Error: ", e)
        return None
    finally:
        client.disconnect()


def set_node_data(node_id: str, value, client: Client = opcua_server()):
    try:
        client.connect()
        node = client.get_node(node_id)
        node.set_value(value)
    except Exception as e:
        print("Error: ", e)
    finally:
        client.disconnect()


if __name__ == '__main__':
    mylevel = get_node_data('ns=6;s=MyLevel')
    if mylevel:
        print(mylevel.Value.Value)

    set_node_data('ns=6;s=MySwitch', True)
    myswitch = get_node_data('ns=6;s=MySwitch')
    if myswitch:
        print(myswitch.Value.Value)

    while True:
        mylevel = get_node_data('ns=6;s=MyLevel')
        if mylevel:
            print(mylevel.Value.Value)
        myswitch = get_node_data('ns=6;s=MySwitch')
        if myswitch.Value.Value == False:
            break
        else:
            time.sleep(1)
