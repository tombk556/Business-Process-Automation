from config import settings
from opcua import Client
import time
import threading
import logging
from .extractors import trigger_action_based_on_auto_id

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

OPCU_URL = settings.opcua_url

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
    client = Client(OPCU_URL)

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
