import requests
from pymongo import MongoClient
from config import settings
from .schemas import InspectionInstance
import logging
import base64

client = MongoClient(settings.mongodb_url)
db = client["BPA_DB"]
collection = db["InspectionData"]
ID = "idShort"  # ID to search for in AAS Shell

OPCU_URL = settings.opcua_url
AAS_URL = settings.aas_url
ID = "idShort"  # ID to search for in AAS Shell



def trigger_action_based_on_auto_id(auto_id, logger: logging.Logger):
    """Method to trigger action based on Auto ID, when the Auto ID is found in the AAS Server

    Args:
        auto_id (str): the auto id fetched from the OPC UA server
        logger (logging.Logger): logger object to log messages
    """
    try:
        response = requests.get(AAS_URL)
        if response.status_code == 200:
            href = search_id_short_and_href(response.json(), auto_id)
            if href:
                ip = href.split("/")[2]
                logger.info(
                    f"Href and IP found in AAS Shell: {ip} for Auto ID: {auto_id}")
                # TODO: More Business Logic here
                # collection.insert_one(InspectionInstance(auto_id=auto_id, ip=ip, href=href).model_dump())
                print("IP: ", ip )
                submodelIdentifier = get_submodelIdentifier(ip)
                print("Submodel Identifier: ", submodelIdentifier)
                inspection_plan = get_inspection_plan(ip, submodelIdentifier)
                print("Inspection Plan: ", inspection_plan)
            else:
                logger.warning(
                    f"Failed to get href for Auto ID <<{auto_id}>> from AAS shell")
        else:
            logger.error(
                f"Failed to trigger action for Auto ID <<{auto_id}>>, status code: {response.status_code}")
    except Exception as e:
        logger.error(
            f"Error triggering action for Auto ID <<{auto_id}>>, error: {e}")


def get_submodelIdentifier(aas_ip_port):
    url = f"http://{aas_ip_port}/submodels?encodedCursor=string&decodedCursor=string&level=deep&extent=withoutBlobValue"
    submodels = get_json_from_url(url)

    result = submodels["result"]
    for model in result:
        if model["idShort"] == "Inspection_Plan":
            id_base64 = encode_to_base64(model["id"])
            return id_base64
    else:
        return None
    
def get_json_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None


def get_inspection_plan(ip_port, submodelIdentifier):
    url = f"http://{ip_port}/submodels/{submodelIdentifier}/submodel-elements/Inspection_Plan/attachment"
    json = get_json_from_url(url)
    if json:
        return json
    else:
        return "No Inspection Plan found"

def encode_to_base64(original_string: str):
    string_bytes = original_string.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def search_id_short_and_href(data, target_id_short) -> str:
    """serach for idShort in the AAS Shell and return the href

    Args:
        data (): data response from the AAS Shell
        target_id_short (_type_): the auto id to search for

    Returns:
        _type_: _description_
    """
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