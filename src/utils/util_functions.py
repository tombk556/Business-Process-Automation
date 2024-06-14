import base64
import json

import os

from config.env_config import settings

cars_config_json_path = os.path.join(settings.main_path, 'cars_config.json')

inspection_plan_response_config_path = os.path.join(settings.main_path, 'inspection_plan_response_config.json')
flask_variables_path = os.path.join(settings.main_path, 'flask_variables.json')


def encode_to_base64(original_string: str):
    string_bytes = original_string.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string


# Cars -------------------------------------
def get_cars_json():
    try:
        with open(cars_config_json_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print('cars config file not found')
        return None


def get_auto_id(rfid):
    """
    get auto_id from rfid
    :param rfid:
    :return:
    """
    # JSON-Datei einlesen
    data = get_cars_json()
    if data:
        # Durchsuchen aller Einträge im Dictionary
        for model, details in data.items():
            # Überprüfen, ob die RFID im aktuellen Modell vorhanden ist
            if any(d.get('RFID') == rfid for d in details):
                # Extrahieren der AutoID, wenn die RFID gefunden wird
                auto_id = next((d.get('AutoID') for d in details if 'AutoID' in d), None)
                return auto_id
    return None


def get_rfid_forSimulation(auto_id):
    # JSON-Datei einlesen
    data = get_cars_json()
    if data:
        # Durchsuchen aller Einträge im Dictionary
        for model, details in data.items():
            # Überprüfen, ob die AutoID im aktuellen Modell vorhanden ist
            if any(d.get('AutoID') == auto_id for d in details):
                # Extrahieren der RFID, wenn die AutoID gefunden wird
                rfid = next((d.get('RFID') for d in details if 'RFID' in d), None)
                rfid_element = f"[]{rfid}\n[]ANT2..." if rfid else None
                return rfid_element
    return None


def get_car_name(auto_id):
    # JSON-Datei einlesen
    data = get_cars_json()
    if data:

        # Durchsuchen aller Einträge im Dictionary
        for model, details in data.items():
            # Überprüfen, ob die AutoID im aktuellen Modell vorhanden ist
            if any(d.get('AutoID') == auto_id for d in details):
                return model
    return None


def save_car_data(data):
    try:
        with open(cars_config_json_path, 'w') as file:
            json.dump(data, file, indent=4)
            return True
    except IOError as e:
        print(f'Failed to write to cars_confing.json: {e}')
    return False


def update_car_data(auto_id_list):
    data_changed = False
    data = get_cars_json()
    if data:
        for auto_id in auto_id_list:
            found = False
            # Durchsuche jedes Auto im JSON
            for key, values in data.items():
                for value in values:
                    if value.get("AutoID", "").replace("_", "").lower() == auto_id.replace("_", "").lower():
                        found = True
                        break
                if found:
                    break

            if not found:
                print(auto_id, "not found")
                # Neuen Schlüsselnamen aus AutoID generieren
                key_name = auto_id.replace('_', ' ')
                # Neues Auto hinzufügen
                data[key_name] = [{"RFID": None}, {"AutoID": auto_id}]
                data_changed = True

    if data_changed:
        return save_car_data(data)


def set_car_rfid(auto_id, new_rfid):
    model_name = get_car_name(auto_id)
    if model_name == "-1":
        print(f'AutoID "{auto_id}" not found in the data.')
        return False

    data = get_cars_json()
    if data and model_name in data:
        for entry in data[model_name]:
            if entry.get("AutoID") == auto_id:
                data[model_name] = [{"RFID": new_rfid}, {"AutoID": auto_id}]
                return save_car_data(data)
    return False


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
