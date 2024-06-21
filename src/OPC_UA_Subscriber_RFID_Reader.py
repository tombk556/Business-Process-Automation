from urllib.parse import urlparse
import re
import socket
import threading
from opcua import Client

from config.env_config import settings
from src.utils.AASManager import AASManager
from src.utils.Logger import SingletonLogger
from src.utils.util_config_cars import get_auto_id

OPCUA_URL_MOCKUP = settings.opcua_url_mockup
OPCUA_URL = settings.opcua_url

simulation_node = "2:RFID-Reader_Data"
node_path = ["2:DeviceSet", "3:PLC_1", "3:DataBlocksGlobal", "3:GDB_OPC-UA", "3:RFID-Reader", "3:Data"]

logger = SingletonLogger()


class OPC_UA_Subscriber:
    """
    A class to manage connections and data subscriptions to an OPC UA server, handling data changes
    and executing callbacks based on the RFID readings from a designated node. This class can operate in
    both simulation and production modes defined by its initialization parameter.

    Attributes:
        is_simulation (bool): Determines if the subscriber will connect to a mock-up or real OPC UA server.
        test_connection_successful (bool): Indicates if the last connection test to the server was successful.
        is_connected (bool): True if the subscriber is currently connected to the server.
        opcua_url (str): The URL to the OPC UA server, determined based on the mode of operation.
        ass_manager (AASManager): An instance of the Asset Administration Shell Manager for handling data.
        latest_auto_id_lock (threading.Lock): A lock for thread-safe operations on the latest_auto_id.
        latest_auto_id (str): The last read auto ID from the OPC UA server.
        client (Client): An OPC UA client connected to the server.
        sub (Subscription): A subscription object for the OPC UA client.
        handler (SubHandler): An inner class instance to handle data change notifications.
        hostname (str): Hostname parsed from the OPC UA URL.
        port (int): Port number parsed from the OPC UA URL.

    Methods:
        __init__(is_simulation=True): Initializes the subscriber, sets up the URL, and connects to the server.
        test_connection(timeout=4): Tests the connection to the OPC UA server with a specified timeout.
        connect(): Establishes a connection with the OPC UA server and subscribes to node changes.
        disconnect(): Disconnects from the OPC UA server and cleans up resources.

    Inner Class:
        SubHandler: Handles data change notifications from the OPC UA server, processes RFID data,
        triggers callbacks, and logs responses based on the inspection plan retrieved using the latest auto ID.
    """


    def __init__(self, is_simulation=True):
        self.is_simulation = is_simulation
        self.test_connection_successful = False
        self.is_connected = False
        if self.is_simulation:
            self.opcua_url = OPCUA_URL_MOCKUP
        else:
            self.opcua_url = OPCUA_URL
        self.ass_manager = AASManager()
        self.latest_auto_id_lock = threading.Lock()
        self.latest_auto_id = None
        self.client = Client(self.opcua_url)
        self.sub = None
        self.handler = self.SubHandler(self)

        parsed_url = urlparse(self.opcua_url)
        self.hostname = parsed_url.hostname
        self.port = parsed_url.port

    class SubHandler:
        def __init__(self, outer):
            self.outer = outer
            self.callback = None

        def datachange_notification(self, node, val, data):
            with self.outer.latest_auto_id_lock:
                if val and val != "None":
                    element_list = val.split("\n")
                    if len(element_list) >= 2:
                        element = element_list[0]
                    else:
                        element = val
                    match = re.search(r'ANT.*', element)
                    if match:
                        rfid_name = match.group()
                        logger.info(f"RFID: {rfid_name}")
                        self.outer.latest_auto_id = get_auto_id(rfid_name)
                        inspection_plan = self.outer.ass_manager.get_inspection_plan(auto_id=self.outer.latest_auto_id)
                        if inspection_plan:
                            if self.callback:
                                inspection_response = self.callback(inspection_plan)
                                self.outer.ass_manager.put_inspection_response(self.outer.latest_auto_id,
                                                                               inspection_response)
                            else:
                                logger.warning("No callback function defined for OPC UA Subscriber.")

                    else:
                        logger.error(f"RFID: {str(val)}")
                        self.outer.latest_auto_id = "None"
                else:
                    logger.error(f"RFID: {str(val)}")
                    self.outer.latest_auto_id = "None"

        def register_callback(self, callback):
            self.callback = callback

    def test_connection(self, timeout=4):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # Timeout für die Verbindung einstellen
        try:
            result = sock.connect_ex((self.hostname, self.port))
            if result == 0:
                self.test_connection_successful = True
                return True  # Der Port ist offen und erreichbar
            else:
                logger.error(f"Lost connection to OPC UA Server!")
                self.test_connection_successful = False
                return False  # Der Port ist geschlossen oder nicht erreichbar
        except socket.error as e:
            self.test_connection_successful = False
            logger.exception(f"Unhandled exception occurred while connecting to OPC UA server!")
            return False
        finally:
            sock.close()

    def connect(self):
        self.test_connection()
        if self.test_connection_successful:
            if not self.is_connected:
                try:
                    self.client.connect()
                    self.is_connected = True
                    logger.info("Connected to OPC UA server")
                    objects = self.client.get_objects_node()
                    if self.is_simulation:
                        auto_id_obj = objects.get_child([simulation_node])
                        auto_id_node = auto_id_obj.get_child([simulation_node])
                    else:
                        auto_id_node = objects.get_child(node_path)
                    self.sub = self.client.create_subscription(100, self.handler)
                    self.sub.subscribe_data_change(auto_id_node)
                except Exception as e:
                    self.is_connected = False
                    logger.exception(f"Unhandled exception occurred while connecting to OPC UA server!")
            else:
                print("already connected")

    def disconnect(self):
        self.is_connected = False
        if self.client and self.test_connection_successful:
            self.client.disconnect()
            logger.info("Disconnected from OPC UA Server")
