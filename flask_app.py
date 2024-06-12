from flask import Flask, render_template
from src.utils.AASManager import AASManager
from src.utils.util_functions import get_car_name
import json
app = Flask(__name__)
ass_manager = AASManager(logger_on=False)


@app.route('/')
def index():
    with open("./config/cars_config.json") as file:
        data = json.load(file)
    return render_template("index.html", vehicles=data)


@app.route('/view_logs/')
def view_logs():
    with open("app.log", "r") as file:
        logs = file.read()
    return render_template("logs.html", logs=logs)


@app.route('/inspection_plan/<auto_id>')
def inspection_plan(auto_id):
    context = {}
    car_name = get_car_name(auto_id)
    data = ass_manager.get_inspection_plan(auto_id)
    context["car_name"] = car_name
    context["auto_id"] = auto_id
    if data:
        context["data"] = data['Inspection_Plan']
    return render_template('inspection_plan.html', **context)


@app.route('/inspection_response/<auto_id>')
def inspection_response(auto_id):
    context = {}
    car_name = get_car_name(auto_id)
    data = ass_manager.get_inspection_response(auto_id)
    context["car_name"] = car_name
    context["auto_id"] = auto_id
    if data:
        context["data"] = data['ResponsePlan']
    return render_template('inspection_response.html', **context)

    
    
if __name__ == '__main__':
    app.run(debug=True)
