import os
import json
from config.env_config import settings
from src.utils.Logger import SingletonLogger

cars_config_json_path = os.path.join(settings.main_path, 'cars_config.json')
logger = SingletonLogger()


def get_cars_json():
    try:
        with open(cars_config_json_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        logger.error(f'cars_config file on {str(cars_config_json_path)} not found')
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
        logger.warning(f'Failed to write to cars_confing.json')
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
                logger.info(f'Car {auto_id} added to cars_confing')

    if data_changed:
        return save_car_data(data)


def set_car_rfid(auto_id, new_rfid):
    model_name = get_car_name(auto_id)
    if not model_name:
        logger.warning(f"AutoID {auto_id} not found in cars_confing. Couldn\'t set the new rfid!")
        return False

    data = get_cars_json()
    if data and model_name in data:
        for entry in data[model_name]:
            if entry.get("AutoID") == auto_id:
                data[model_name] = [{"RFID": new_rfid}, {"AutoID": auto_id}]
                return save_car_data(data)
    return False


# Simulation
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

