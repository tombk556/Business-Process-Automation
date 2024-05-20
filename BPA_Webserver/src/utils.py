from config import settings
from opcua import Client
import requests
import time
import threading
import logging
import sys
from pymongo import MongoClient
from .schemas import InspectionInstance

sys.path.append('../')
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

OPCU_URL = settings.opcua_url
AAS_URL = settings.aas_url
ID = "idShort"  # ID to search for in AAS Shell

latest_auto_id_lock = threading.Lock()
latest_auto_id = None

client = MongoClient(settings.mongodb_url)
db = client["BPA_DB"]
collection = db["InspectionData"]

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        global latest_auto_id
        with latest_auto_id_lock:
            latest_auto_id = val
        trigger_action_based_on_auto_id(val)


def trigger_action_based_on_auto_id(auto_id):
    try:
        response = requests.get(AAS_URL, params={'auto_id': auto_id})
        if response.status_code == 200:
            href = search_id_short_and_href(response.json(), auto_id)
            if href:
                logger.info(
                    f"Href found in AAS Shell: {href} for Auto ID: {auto_id}")
                collection.insert_one(InspectionInstance(auto_id=auto_id, href=href).model_dump())
            else:
                logger.warning(
                    f"Failed to get href for Auto ID <<{auto_id}>> from AAS shell")
        else:
            logger.error(
                f"Failed to trigger action for Auto ID <<{auto_id}>>, status code: {response.status_code}")
    except Exception as e:
        logger.error(
            f"Error triggering action for Auto ID <<{auto_id}>>, error: {e}")


def search_id_short_and_href(data, target_id_short):
    if isinstance(data, dict):
        if data.get(ID) == target_id_short:
            endpoints = data.get("endpoints")
            if endpoints:
                return endpoints[0].get("protocolInformation", {}).get("href")
        for value in data.values():
            if isinstance(value, (dict, list)):
                result = search_id_short_and_href(value, target_id_short)
                if result:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = search_id_short_and_href(item, target_id_short)
            if result:
                return result
    return None


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
