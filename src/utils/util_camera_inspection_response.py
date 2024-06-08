def get_simplified_inspection_response(data_in, schwellwert=0.6):
    detections = _transform_detections(data_in)
    return _get_simplified_inspection_response(detections, schwellwert)


def get_value(simplified_data_in, key, sub):
    if key in simplified_data_in:
        return simplified_data_in[key][sub]
    else:
        # Rückgabe einer Nachricht, wenn der Schlüssel nicht gefunden wird
        # logger TODO
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
