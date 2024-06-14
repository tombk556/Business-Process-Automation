import json
import threading
import time

from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from InspectionHandler import InspectionHandler
from src.utils.AASManager import AASManager
from src.utils.util_functions import get_car_name, get_cars_json, update_car_data, set_car_rfid

app = Flask(__name__)


def run_handler():
    handler.start()


@app.route('/switch_settings/', methods=['POST'])
def handle_switch():
    global handler, handler_thread
    is_simulation = request.form.get('is_simulation') == 'true'
    print(f"is_simulation: {is_simulation}")
    if handler.is_connected:
        stop_inspection()
    handler = InspectionHandler(is_simulation=is_simulation)
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    context = {}
    if request.method == 'POST':
        rfid = request.form['RFID'] if 'RFID' in request.form else None
        auto_id = request.form['autoId'] if 'autoId' in request.form else None
        if rfid is not None and auto_id is not None:
            set_car_rfid(auto_id, rfid)
    if ass_manager.test_connection_successful:
        auto_id_list = ass_manager.get_all_idShorts()
        update_car_data(auto_id_list)
    data = get_cars_json()
    context["vehicles"] = data
    context["handler_connected"] = handler.is_connected
    context["is_simulation"] = handler.is_simulation
    inspection_handler_status = "active" if handler.is_connected else "inactive"
    inspection_handler_status = "not connected" if not handler.test_connection_successful else inspection_handler_status
    context["inspection_handler_status"] = inspection_handler_status
    context["ass_connection"] = ass_manager.test_connection_successful
    return render_template("index.html", **context)


@app.route('/connect_inspection/')
def connect_inspection():
    handler.test_connection()
    if handler.test_connection_successful:
        return 'connection test successful'
    else:
        return "connection test failed"


@app.route('/start_inspection/')
def start_inspection():
    global handler_thread
    if not handler.is_connected:
        if handler_thread is None:
            try:
                handler_thread = threading.Thread(target=run_handler)
                handler_thread.start()
                time.sleep(1)
            except Exception as e:
                return f"failed"
            finally:
                return "active"
    return "already active"


@app.route('/stop_inspection/')
def stop_inspection():
    global handler_thread
    if handler.is_connected and handler_thread is not None:
        handler.stop()  # Assuming there is a safe .stop() method
        handler_thread.join()  # Wait for the thread to finish
        handler_thread = None
        time.sleep(1)
        return "inactive"
    else:
        return "already inactive"


@app.route('/inspection_plan/<auto_id>/')
def inspection_plan(auto_id):
    context = {}
    car_name = get_car_name(auto_id)
    if ass_manager.test_connection_successful:
        data = ass_manager.get_inspection_plan(auto_id)
        if data:
            print(json.dumps(data, indent=4))
            context["data"] = data['Inspection_Plan'] if 'Inspection_Plan' in data else None
        else:
            context["warning"] = "No Inspection Plan was found!\n Check the AAS connection!"
            ass_manager.test_connection()
    else:
        ass_manager.test_connection()
        if ass_manager.test_connection_successful:
            context["warning"] = "Please reload this site!"
        else:
            context["warning"] = "Couldn't connect to AAS!"
    context["car_name"] = car_name
    context["auto_id"] = auto_id
    return render_template('inspection_plan.html', **context)


@app.route('/inspection_response/<auto_id>/')
def inspection_response(auto_id):
    context = {}
    car_name = get_car_name(auto_id)
    if ass_manager.test_connection_successful:
        data = ass_manager.get_inspection_response(auto_id)
        if data:
            print(json.dumps(data, indent=4))
            context["data"] = data['Response_Plan'] if 'Response_Plan' in data else None
        else:
            context["warning"] = "No Inspection Response was found!\n Check the AAS connection!"
            ass_manager.test_connection()
    else:
        ass_manager.test_connection()
        if ass_manager.test_connection_successful:
            context["warning"] = "Please reload this site!"
        else:
            context["warning"] = "Couldn't connect to AAS!"
    context["car_name"] = car_name
    context["auto_id"] = auto_id
    return render_template('inspection_response.html', **context)


@app.route('/check_aas_connection/')
def check_aas_connection_status():
    ass_manager.test_connection()
    return 'successful' if ass_manager.test_connection_successful else 'unavailable'


@app.route('/view_logs/')
def view_logs():
    return render_template("view_logs.html")


@app.route('/log-content/')
def log_content():
    try:
        with open("app.log", "r") as file:
            lines = file.readlines()
        return jsonify(log_content=lines)
    except Exception as e:
        return abort(500)


@app.route('/reset_logs/')
def reset_logs():
    try:
        with open("app.log", "r") as file:
            lines = file.readlines()

        last_lines = lines[-2:] if len(lines) >= 2 else lines
        with open("app.log", "w") as file:
            file.writelines(last_lines)
    except Exception as e:
        print(f"Failed to truncate main log file!")
    return redirect(url_for('view_logs'))


if __name__ == '__main__':
    ass_manager = AASManager(logger_on=False)
    handler = InspectionHandler(is_simulation=True)
    handler_thread = None
    app.run(debug=False)
