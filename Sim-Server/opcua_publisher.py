from opcua import ua, Server
import time
import threading

bmws = [
    "BMW_x7",
    "bmw_m4",
    "bmw_5er_coupe",
]

server = Server()
url = "opc.tcp://0.0.0.0:4840"  # replace with the actual IP address of the OPCUA server
server.set_endpoint(url)

name = "BMWFactory"
addspace = server.register_namespace(name)

objects = server.get_objects_node()

auto_id_obj = objects.add_object(addspace, "AutoID")
auto_id = auto_id_obj.add_variable(addspace, "AutoID", "No Data")
auto_id.set_writable()

def input_listener():
    while True:
        new_auto_id = input("Enter new car ID: ")
        auto_id.set_value(new_auto_id)
        print(new_auto_id + " published to OPC UA server")

if __name__ == '__main__':
    server.start()
    print(f"Server started at {url}")
    try:
        input_thread = threading.Thread(target=input_listener)
        input_thread.daemon = True
        input_thread.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopping...")
    finally:
        server.stop()
        print("Server stopped")
