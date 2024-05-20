import requests
from pymongo import MongoClient
from config import settings
from .schemas import InspectionInstance
import logging

client = MongoClient(settings.mongodb_url)
db = client["BPA_DB"]
collection = db["InspectionData"]
ID = "idShort"  # ID to search for in AAS Shell

OPCU_URL = settings.opcua_url
AAS_URL = settings.aas_url
ID = "idShort"  # ID to search for in AAS Shell

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


def trigger_action_based_on_auto_id(auto_id, logger: logging.Logger):
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