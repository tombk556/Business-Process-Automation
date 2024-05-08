from flask import Flask
import threading
import time
import sys

sys.path.append('../')
from src.subscriber import OPCUASubscriber

app = Flask(__name__)

subscriber = OPCUASubscriber(server_url="opc.tcp://uademo.prosysopc.com:53530/OPCUA/SimulationServer",
                             node_id="ns=6;s=MySwitch")

opcua_thread = threading.Thread(target=subscriber.run)


@app.route('/')
def index():
    return "Hallo, Flask läuft!"


def start_app():
    opcua_thread.start()
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    start_app()
