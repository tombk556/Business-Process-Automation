import json
import threading
import time

from flask import Flask, render_template, redirect, url_for, request

from InspectionHandler import InspectionHandler
from src.utils.AASManager import AASManager
from src.utils.util_functions import get_car_name, get_cars_json, update_car_data, set_car_rfid

app = Flask(__name__)
ass_manager = AASManager(logger_on=False)
handler = InspectionHandler(is_simulation=True)
handler_thread = None


def run_handler():
    handler.start()


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
                return "active!"
    return "already active!"


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


@app.route('/', methods=['GET', 'POST'])
def index():
    context = {}
    if request.method == 'POST':
        rfid = request.form['RFID'] if 'RFID' in request.form else None
        auto_id = request.form['autoId'] if 'autoId' in request.form else None
        if rfid is not None and auto_id is not None:
            set_car_rfid(auto_id, rfid)
    auto_id_list = ass_manager.get_all_idShorts()
    update_car_data(auto_id_list)
    data = get_cars_json()
    context["vehicles"] = data
    context["handler_connected"] = handler.is_connected

    inspection_handler_status = "active" if handler.is_connected else "inactive"
    inspection_handler_status = "not connected" if not handler.test_connection_successful else inspection_handler_status
    context["inspection_handler_status"] = inspection_handler_status
    return render_template("index.html", **context)


@app.route('/change_car_rfid/<auto_id>/<rfid>/')
def change_car_rfid(auto_id, rfid):
    set_car_rfid(auto_id, rfid)
    return redirect(url_for('index'))


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
    print(json.dumps(data, indent=4))
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
    print(json.dumps(data, indent=4))
    context["car_name"] = car_name
    context["auto_id"] = auto_id
    if data:
        context["data"] = data['Response_Plan'] if 'Response_Plan' in data else None
    return render_template('inspection_response.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
