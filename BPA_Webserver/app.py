from flask import Flask
import threading
import time
import sys
sys.path.append('../')
from src.subscriber import OPCUASubscriber


app = Flask(__name__)
 
subscriber = OPCUASubscriber(server_url="opc.tcp://uademo.prosysopc.com:53530/OPCUA/SimulationServer", 
                              node_id="ns=6;s=MySwitch")
 
test_thread = threading.Thread(target=subscriber.run)
 
@app.route('/')
def index():
    return "Hallo, Flask läuft!"
 
# Die Funktion zum Starten der Flask-App und des Threads
def start_app():
    # Thread starten
    test_thread.start()
    # Flask-Server starten
    app.run(debug=True, use_reloader=False)  # use_reloader=False ist wichtig, um Konflikte mit dem Thread zu vermeiden
 
if __name__ == '__main__':
    start_app()