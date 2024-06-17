import os
import json
from config.env_config import settings
from src.utils.Logger import SingletonLogger

cars_config_json_path = os.path.join(settings.config_path, 'cars_config.json')
logger = SingletonLogger()


def get_cars_json():
    """
    Retrieves the cars configuration data from a JSON file specified by the configuration path.

    This function attempts to load a JSON file that contains configuration data for various car models,
    handling and logging any file not found errors.

    Returns:
        dict or None: A dictionary containing cars configuration data, or None if the file is not found.

    Example:
        cars_data = get_cars_json()
    """
    try:
        with open(cars_config_json_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        logger.error(f'cars_config file on {str(cars_config_json_path)} not found')
        return None


def get_auto_id(rfid):
    """
    Retrieves the auto ID associated with a given RFID from the cars configuration.

    This function searches through a preloaded cars configuration JSON to find the auto ID corresponding
    to the specified RFID code.

    Args:
        rfid (str): The RFID code to search for in the car configurations.

    Returns:
        str or None: The auto ID if found; otherwise, None.

    Example:
        auto_id = get_auto_id('12345RFIDCode')
    """
    data = get_cars_json()
    if data:
        for model, details in data.items():
            if any(d.get('RFID') == rfid for d in details):
                auto_id = next((d.get('AutoID') for d in details if 'AutoID' in d), None)
                return auto_id
    return None


def get_car_name(auto_id):
    """
    Retrieves the car model name associated with a specific auto ID from the cars configuration.

    Args:
        auto_id (str): The auto ID to search for in the car configurations.

    Returns:
        str or None: The name of the car model if found; otherwise, None.

    Example:
        car_name = get_car_name('AU123ID')
    """
    data = get_cars_json()
    if data:

        for model, details in data.items():
            if any(d.get('AutoID') == auto_id for d in details):
                return model
    return None


def save_car_data(data):
    """
    Saves the provided cars configuration data back to the JSON file.

    Args:
        data (dict): The car configuration data to save.

    Returns:
        bool: True if data is successfully written; False otherwise due to an IO error.

    Example:
        success = save_car_data(modified_data)
    """
    try:
        with open(cars_config_json_path, 'w') as file:
            json.dump(data, file, indent=4)
            return True
    except IOError as e:
        logger.warning(f'Failed to write to cars_confing.json')
    return False


def update_car_data(auto_id_list):
    """
    Updates or adds new car data for the provided list of auto IDs in the cars configuration.

    Args:
        auto_id_list (list of str): List of auto IDs to update or add in the configuration.

    Returns:
        bool or None: True if the configuration was updated and saved successfully; None otherwise.

    Example:
        updated = update_car_data(['AU123ID', 'AU456ID'])
    """
    data_changed = False
    data = get_cars_json()
    if data:
        for auto_id in auto_id_list:
            found = False
            for key, values in data.items():
                for value in values:
                    if value.get("AutoID", "").replace("_", "").lower() == auto_id.replace("_", "").lower():
                        found = True
                        break
                if found:
                    break

            if not found:
                key_name = auto_id.replace('_', ' ')
                data[key_name] = [{"RFID": None}, {"AutoID": auto_id}]
                data_changed = True
                logger.info(f'Car {auto_id} added to cars_confing')

    if data_changed:
        return save_car_data(data)


def set_car_rfid(auto_id, new_rfid):
    """
    Updates the RFID for a specified auto ID in the car configuration.

    Args:
        auto_id (str): The auto ID whose RFID needs to be updated.
        new_rfid (str): The new RFID to assign to the auto ID.

    Returns:
        bool: True if the RFID is updated and saved successfully; False otherwise.

    Example:
        success = set_car_rfid('AU123ID', 'new12345RFIDCode')
    """
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


def get_rfid_forSimulation(auto_id):
    """
    Retrieves the RFID for a specified auto ID for simulation purposes.

    This function is primarily used in a simulated environment to fetch the RFID associated with an auto ID,
    formatted specifically for simulation outputs.

    Args:
        auto_id (str): The auto ID whose RFID is needed for simulation.

    Returns:
        str or None: The formatted RFID string if found; otherwise, None.

    Example:
        rfid_sim = get_rfid_forSimulation('AU123ID')
    """
    data = get_cars_json()
    if data:
        for model, details in data.items():
            if any(d.get('AutoID') == auto_id for d in details):
                rfid = next((d.get('RFID') for d in details if 'RFID' in d), None)
                rfid_element = f"[]{rfid}\n[]ANT2..." if rfid else None
                return rfid_element
    return None

