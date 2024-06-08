import base64
import json

import os

from config.env_config import settings

cars_config_json_path = os.path.join(settings.main_path, 'cars_config.json')

inspection_plan_response_config_path = os.path.join(settings.main_path, 'inspection_plan_response_config.json')


def encode_to_base64(original_string: str):
    string_bytes = original_string.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string


# Cars -------------------------------------
def get_auto_id(rfid):
    """
    get auto_id from rfid
    :param rfid:
    :return:
    """
    # JSON-Datei einlesen
    with open(cars_config_json_path, 'r') as file:
        data = json.load(file)

    # Durchsuchen aller Einträge im Dictionary
    for model, details in data.items():
        # Überprüfen, ob die RFID im aktuellen Modell vorhanden ist
        if any(d.get('RFID') == rfid for d in details):
            # Extrahieren der AutoID, wenn die RFID gefunden wird
            auto_id = next((d.get('AutoID') for d in details if 'AutoID' in d), None)
            return auto_id
    return "-1"


def get_rfid_forSimulation(auto_id):
    # JSON-Datei einlesen

    with open(cars_config_json_path, 'r') as file:
        data = json.load(file)

        # Durchsuchen aller Einträge im Dictionary
        for model, details in data.items():
            # Überprüfen, ob die AutoID im aktuellen Modell vorhanden ist
            if any(d.get('AutoID') == auto_id for d in details):
                # Extrahieren der RFID, wenn die AutoID gefunden wird
                rfid = next((d.get('RFID') for d in details if 'RFID' in d), None)
                rfid_element = f"[]{rfid}\n[]ANT2..."
                return rfid_element
        return "-1"


# Inspection Plan -----------

def get_camera_response_key(inspection_plan_key):
    """
    get camera response key from inspection_plan key
    :param inspection_plan_key:
    :return:
    """
    try:
        with open(inspection_plan_response_config_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Datei nicht gefunden.")
        data = {}
    except json.JSONDecodeError:
        print("Fehler beim Parsen der JSON-Daten.")
        data = {}
    return data.get(inspection_plan_key, None)
