from src.utils.util_camera_inspection_response import get_value
from src.utils.util_functions import get_camera_response_key


def get_response_plan(inspection_plan, inspection_response_simplified):
    inspection_plan_part = inspection_plan['Inspection_Plan']
    response_plan = {
        "ResponsePlan": {}
    }
    response_plan_part = response_plan["ResponsePlan"]
    # Durchgehen des 'Inspection_Plan'-Teils
    for class_name, details in inspection_plan_part.items():
        response_plan_part[class_name] = {}
        camera_key = get_camera_response_key(class_name)

        for sub_category, value in details.items():
            if "in_place" in sub_category:
                sub = "in_place"
            elif "free_of_damage" in sub_category:
                sub = "free_of_damage"
            elif "has_correct_color" in sub_category:  # wird None sein, da CameraResponse die Daten nicht liefert!
                sub = "has_correct_color"
            else:
                sub = sub_category

            new_val = get_value(inspection_response_simplified, camera_key, sub)
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
