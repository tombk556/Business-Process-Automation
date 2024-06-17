import json
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from InspectionHandler import InspectionHandler
from src.utils.AASManager import AASManager
from src.utils.util_config_cars import get_car_name, get_cars_json, update_car_data, set_car_rfid

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Serves the main page of the application, handles POST to update RFID settings,
    and dynamically updates car data from the AAS.
    """
    context = {}
    if request.method == 'POST':
        rfid = request.form['RFID'] if 'RFID' in request.form else None
        auto_id = request.form['autoId'] if 'autoId' in request.form else None
        if rfid is not None and auto_id is not None:
            set_car_rfid(auto_id, rfid)
    if aas_manager.test_connection_successful:
        auto_id_list = aas_manager.get_all_idShorts()
        update_car_data(auto_id_list)
    data = get_cars_json()
    context["vehicles"] = data
    context["handler_connected"] = handler.is_connected
    context["is_simulation"] = handler.is_simulation
    if handler.is_connected and not handler.opcua_subscriber.test_connection_successful:
        handler.stop()
    inspection_handler_status = "active" if handler.is_connected else "inactive"
    inspection_handler_status = "not connected" if not handler.test_connection_successful else inspection_handler_status
    context["inspection_handler_status"] = inspection_handler_status
    context["aas_connection"] = aas_manager.test_connection_successful
    return render_template("index.html", **context)


@app.route('/switch_settings/', methods=['POST'])
def handle_switch():
    """
    Handles the switch between simulation and actual OPC UA server settings.
    """
    global handler
    is_simulation = request.form.get('is_simulation') == 'true'
    if handler.is_connected:
        stop_inspection()
    handler = InspectionHandler(is_simulation=is_simulation)
    return redirect(url_for('index'))


@app.route('/check_aas_connection/')
def check_aas_connection_status():
    """
    Checks and returns the connection status of the Asset Administration Shell (AAS).
    """
    aas_manager.test_connection()
    return 'successful' if aas_manager.test_connection_successful else 'unavailable'


@app.route('/check_connection/')
def check_connection():
    """
    Performs a connection test for the main inspection handler and returns the status.
    """
    handler.test_connection()
    if handler.test_connection_successful:
        return 'connection test successful'
    else:
        return "connection test failed"


@app.route('/start_inspection/')
def start_inspection():
    """
    Initiates the inspection process if not already active.
    """
    global handler
    if not handler.is_connected:
        return handler.start()
    else:
        return 'already active'


@app.route('/stop_inspection/')
def stop_inspection():
    """
    Stops the ongoing inspection process if currently active.
    """
    global handler
    if handler.is_connected:
        return handler.stop()
    else:
        return "already inactive"


@app.route('/inspection_plan/<auto_id>/')
def inspection_plan(auto_id):
    """
    Retrieves and displays the inspection plan for a specified auto ID.
    """
    context = {}
    car_name = get_car_name(auto_id)
    if aas_manager.test_connection_successful:
        data = aas_manager.get_inspection_plan(auto_id)
        if data:
            context["data"] = data['Inspection_Plan'] if 'Inspection_Plan' in data else print(
                json.dumps(data, indent=4))
        else:
            context["warning"] = "No Inspection Plan was found!\n Check the AAS connection!"
            aas_manager.test_connection()
    else:
        aas_manager.test_connection()
        if aas_manager.test_connection_successful:
            context["warning"] = "Please reload this site!"
        else:
            context["warning"] = "Couldn't connect to AAS!"
    context["car_name"] = car_name
    context["auto_id"] = auto_id
    return render_template('inspection_plan.html', **context)


@app.route('/inspection_response/<auto_id>/')
def inspection_response(auto_id):
    """
    Retrieves and displays the inspection response for a specified auto ID.
    """
    context = {}
    car_name = get_car_name(auto_id)
    if aas_manager.test_connection_successful:
        data = aas_manager.get_inspection_response(auto_id)
        if data:
            context["data"] = data['Response_Plan'] if 'Response_Plan' in data else print(json.dumps(data, indent=4))
        else:
            context["warning"] = "No Inspection Response was found!\n Check the AAS connection!"
            aas_manager.test_connection()
    else:
        aas_manager.test_connection()
        if aas_manager.test_connection_successful:
            context["warning"] = "Please reload this site!"
        else:
            context["warning"] = "Couldn't connect to AAS!"
    context["car_name"] = car_name
    context["auto_id"] = auto_id
    return render_template('inspection_response.html', **context)


@app.route('/view_logs/')
def view_logs():
    """
    Displays the logs page to view application logs.
    """
    return render_template("view_logs.html")


@app.route('/log-content/')
def log_content():
    """
    Fetches and returns the content of the log file.
    """
    try:
        with open("app.log", "r") as file:
            lines = file.readlines()
        return jsonify(log_content=lines)
    except Exception as e:
        return abort(500)


@app.route('/reset_logs/')
def reset_logs():
    """
    Resets the log file to only keep the last few entries.
    """
    try:
        with open("app.log", "r") as file:
            lines = file.readlines()
        last_lines = lines[-2:] if len(lines) >= 2 else lines
        with open("app.log", "w") as file:
            file.writelines(last_lines)
    except Exception as e:
        print(f"Failed to reset the log file!")
    return redirect(url_for('view_logs'))


if __name__ == '__main__':
    aas_manager = AASManager(logger_on=False)
    handler = InspectionHandler(is_simulation=True)
    app.run(debug=False, port=3000, host="0.0.0.0")
