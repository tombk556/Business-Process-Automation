from opcua import ua, Server
import random
import time
import uuid

bmws = ["BMW X7",
        "BMW M4",
        "BMW 5er Coupe",
        "BMW 3er Limousine",
        "BMW 1er Limousine",
        "BMW 7er Limousine",
        "BMW X5"]

server = Server()
url = "opc.tcp://0.0.0.0:4840" # replace with actual IP address of the OPCUA server 
server.set_endpoint(url)

name = "BMWFactory"
addspace = server.register_namespace(name)

objects = server.get_objects_node()

auto_id_obj = objects.add_object(addspace, "AutoID")
auto_id = auto_id_obj.add_variable(addspace, "AutoID", "No Data")
auto_id.set_writable()

def rfid_sim_reader():
    while True:
        new_auto_id = str(uuid.uuid4()) + " " + random.choice(bmws)
        auto_id.set_value(new_auto_id)
        print(new_auto_id + " published to OPC UA server")
        time.sleep(10)

if __name__ == '__main__':
    server.start()
    print(f"Server started at {url}")
    try:
        rfid_sim_reader()
    finally:
        server.stop()
        print("Server stopped")
