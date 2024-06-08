import re
import time
import threading
from opcua import Client

from config.env_config import settings
from src.utils.AASManager import AASManager
from src.utils.Logger import SingletonLogger
from src.utils.util_functions import get_auto_id

OPCUA_URL_MOCKUP = settings.opcua_url_mockup
OPCUA_URL = settings.opcua_url

simulation_node = "2:RFID-Reader_Data"
node_path = ["2:DeviceSet", "3:PLC_1", "3:DataBlocksGlobal", "3:GDB_OPC-UA", "3:RFID-Reader", "3:Data"]

logger = SingletonLogger()


class OPC_UA_Subscriber:
    def __init__(self, is_simulation=True):
        self.is_simulation = is_simulation
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

    class SubHandler:
        def __init__(self, outer):
            self.outer = outer
            self.callback = None

        def datachange_notification(self, node, val, data):
            with self.outer.latest_auto_id_lock:
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
                    # print(f"Auto ID: {self.outer.latest_auto_id}")
                    inspection_plan = self.outer.ass_manager.get_inspection_plan(auto_id=self.outer.latest_auto_id)

                    # Aufrufen der Callback-Funktion, wenn sie existiert
                    if self.callback:
                        inspection_response = self.callback(inspection_plan)
                        self.outer.ass_manager.put_inspection_response(self.outer.latest_auto_id,
                                                                       inspection_response)

                else:
                    self.outer.latest_auto_id = "-1"

        def register_callback(self, callback):
            self.callback = callback

    def connect(self):
        try:
            self.client.connect()
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
            logger.exception(f"Error connecting to OPC UA server, error: {e}")
            self.disconnect()

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping OPC UA Subscriber.")

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            logger.info("Disconnected from OPC UA server")
