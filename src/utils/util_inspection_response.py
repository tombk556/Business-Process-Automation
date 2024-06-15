import json
import os
from config.env_config import settings

inspection_plan_response_config_path = os.path.join(settings.config_path, 'inspection_plan_response_config.json')


def create_response_plan(inspection_plan, inspection_response_simplified):
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
    detections = _transform_detections(data_in)
    return _get_simplified_inspection_response(detections, schwellwert)


def _get_camera_response_key(inspection_plan_key):
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


def _get_value(simplified_data_in, key, sub):
    if key in simplified_data_in:
        return simplified_data_in[key][sub]
    else:
        return None


def _transform_detections(json_data):
    """
    Transforms the detections returned from original data
    :param json_data:
    :return:
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
    Bewertet jede Klasse basierend auf Erkennungskonfidenz und Schadensfreiheit.

    Args:
        transformed_json_in (dict): Das Dictionary, das die Klassen und ihre Erkennungsdaten enthält.
        param_schwellwert (float, optional): Der Schwellwert für die Erkennungskonfidenz, default ist 0.6.

    Returns:
        dict: Ein Dictionary, das für jede Klasse die Klassen-ID und den Zufriedenheitsstatus enthält.
              'is_satisfying' ist True, wenn die Erkennungskonfidenz über dem Schwellwert liegt und das Objekt schadensfrei ist.
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
