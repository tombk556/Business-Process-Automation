from flask import Blueprint
import requests

service_one = Blueprint('service_one', __name__, url_prefix='/service_one')

@service_one.route('/', methods=['GET', 'POST'])
def home():
    data = _get_plan(url="http://141.56.180.118:8081/submodels")
    return data



def _get_plan(url):
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return {
                "Status": response.status_code,
                "Error Response": response.json()
            }
        else:
            return response.json()

    except Exception as error:
        return {
            "Status": "Intenal Server Error",
            "Error Response": error
        }