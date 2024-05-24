import time
import threading
from opcua import Client
from config import settings
from .extractors import trigger_action_based_on_auto_id
from .logging import setup_logging

# Setup logging
logger = setup_logging()

OPCUA_URL = settings.opcua_url

latest_auto_id_lock = threading.Lock()
latest_auto_id = None

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        global latest_auto_id
        with latest_auto_id_lock:
            latest_auto_id = val
        trigger_action_based_on_auto_id(auto_id=val, logger=logger)

def opcua_subscriber():
    global latest_auto_id
    client = Client(OPCUA_URL)

    try:
        client.connect()
        logger.info("Connected to OPC UA server")

        objects = client.get_objects_node()

        auto_id_obj = objects.get_child(["2:AutoID"])
        auto_id_node = auto_id_obj.get_child(["2:AutoID"])

        handler = SubHandler()
        sub = client.create_subscription(100, handler)

        sub.subscribe_data_change(auto_id_node)

        while True:
            time.sleep(1)

    except Exception as e:
        logger.exception(f"Error subscribing to OPC UA server, error: {e}")

    finally:
        client.disconnect()
        logger.info("Disconnected from OPC UA server")

if __name__ == "__main__":
    opcua_subscriber()
