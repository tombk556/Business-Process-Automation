import json
import os
from config.env_config import settings

inspection_plan_response_config_path = os.path.join(settings.config_path, 'inspection_plan_response_config.json')


def create_response_plan(inspection_plan, inspection_response_simplified):
    """
    Generates a response plan based on an inspection plan and simplified inspection responses.
    
    This function maps inspection responses to the relevant sections of an inspection plan,
    considering specific conditions and keys to update the response accordingly.

    Args:
        inspection_plan (dict): Dictionary containing details of the inspection plan.
        inspection_response_simplified (dict): Simplified responses from the inspection camera.

    Returns:
        dict: A dictionary containing the updated response plan based on the provided inspection inputs.

    Example:
        response_plan = create_response_plan(inspection_details, simplified_responses)
    """
    inspection_plan_part = inspection_plan['Inspection_Plan']
    response_plan = {
        "Response_Plan": {}
    }
    response_plan_part = response_plan["Response_Plan"]
    # Durchgehen des 'Inspection_Plan'-Teils
    for class_name, details in inspection_plan_part.items():
        response_plan_part[class_name] = {}
        camera_key = _get_camera_response_key(class_name)

        for sub_category, value in details.items():
            if "in_place" in sub_category:
                sub = "in_place"
            elif "free_of_damage" in sub_category:
                sub = "free_of_damage"
            elif "has_correct_color" in sub_category:  # wird None sein, da CameraResponse die Daten nicht liefert!
                sub = "has_correct_color"
            else:
                sub = sub_category

            new_val = _get_value(inspection_response_simplified, camera_key, sub)
            if new_val is True:
                response_plan_part[class_name][sub_category] = new_val
            elif new_val is False:
                response_plan_part[class_name][sub_category] = new_val
            else:
                if None in value:
                    response_plan_part[class_name][sub_category] = None
                else:
                    response_plan_part[class_name][sub_category] = False
    return response_plan


def get_simplified_inspection_response(data_in, schwellwert=0.6):
    """
    Simplifies raw inspection data into a more manageable format based on a threshold confidence value.

    This function processes raw detection data to evaluate which items meet specified confidence and
    condition thresholds. It uses internal functions to transform detections and generate a simplified response.

    Args:
        data_in (dict): Raw data containing detections from an inspection.
        schwellwert (float, optional): The threshold for determining if a detection is significant, default is 0.6.

    Returns:
        dict: A dictionary with simplified inspection responses keyed by class name.
    
    Example:
        simplified_response = get_simplified_inspection_response(raw_data)
    """
    detections = _transform_detections(data_in)
    return _get_simplified_inspection_response(detections, schwellwert)


def _get_camera_response_key(inspection_plan_key):
    """
    Retrieves the corresponding camera response key for a given inspection plan key from a configuration file.

    This function looks up a mapping in a JSON configuration file that translates inspection plan keys to
    camera response keys, which are used to align inspection data with the respective camera outputs.

    Args:
        inspection_plan_key (str): The key used in the inspection plan to identify a specific inspection criteria or item.

    Returns:
        str or None: The corresponding camera response key if found, otherwise None.

    Example:
        camera_key = _get_camera_response_key('front_bumper_inspection')

    Raises:
        FileNotFoundError: If the configuration file does not exist at the specified path.
        json.JSONDecodeError: If there are errors decoding the JSON data from the configuration file.
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


def _get_value(simplified_data_in, key, sub):
    """
    Retrieves a specific value from a nested dictionary based on a provided key and subkey.

    This function is typically used to fetch specific attribute values from a simplified inspection data dictionary,
    where the key represents a high-level classification and the subkey a specific attribute of interest.

    Args:
        simplified_data_in (dict): The dictionary containing the simplified inspection data.
        key (str): The primary key under which data is stored.
        sub (str): The subkey associated with the specific attribute to retrieve.

    Returns:
        Any: The value associated with the 'sub' key under the main 'key' in the dictionary, or None if not found.

    Example:
        value = _get_value(simplified_inspection_data, 'engine', 'in_place')
    """
    if key in simplified_data_in:
        return simplified_data_in[key][sub]
    else:
        return None


def _transform_detections(json_data):
    """
    Transforms detection data structured by individual detections into a dictionary keyed by class names.
    
    This function reorganizes raw detection data from JSON format into a more structured dictionary. Each class
    from the detections is mapped to its most recent detection metrics such as confidence and damage status.

    Args:
        json_data (dict): The original JSON data containing detection information.

    Returns:
        dict: A dictionary where each key is a class name, and the value is another dictionary containing
              'class_id', 'detection_confidence', and 'free_of_damage' for the latest detection of that class.

    Example:
        transformed_data = _transform_detections(raw_json_data)
    """
    # Umformatieren der detections, organisiert nach class_name
    detections_by_class = {}
    for detection in json_data["detections"]:
        detection_confidence = detection[0]
        is_free_of_damage = detection[1]
        class_id = detection[2]
        class_name = json_data["classes"][str(class_id)]

        # Aktualisieren mit dem letzten verfügbaren Wert für jede Klasse
        detections_by_class[class_name] = {
            "class_id": class_id,
            "detection_confidence": detection_confidence,
            "free_of_damage": is_free_of_damage
        }

    return detections_by_class


def _get_simplified_inspection_response(transformed_json_in, param_schwellwert=0.6):
    """
    Evaluates each class based on detection confidence and damage status to determine satisfaction.

    This function assesses each detection by comparing its detection confidence against a specified threshold
    and whether the item is free of damage, to classify if the detection is satisfying.

    Args:
        transformed_json_in (dict): A dictionary containing transformed detection data keyed by class names.
        param_schwellwert (float, optional): The confidence threshold for determining satisfaction, defaults to 0.6.

    Returns:
        dict: A dictionary that indicates for each class whether it meets the criteria of being 'in_place' 
              (detection confidence above threshold) and 'free_of_damage'.

    Example:
        simplified_response = _get_simplified_inspection_response(transformed_data)
    """
    inspection_results = {}
    for class_name, details in transformed_json_in.items():
        detection_confidence = details["detection_confidence"]
        class_id = details["class_id"]
        free_of_damage = details["free_of_damage"]

        in_place = detection_confidence > param_schwellwert
        inspection_results[class_name] = {
            "class_id": class_id,
            "in_place": in_place,
            "free_of_damage": free_of_damage
        }
    return inspection_results
