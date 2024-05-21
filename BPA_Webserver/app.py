from flask import Flask
import threading
import sys

sys.path.append('..')
from src.utils import opcua_subscriber, latest_auto_id, latest_auto_id_lock

app = Flask(__name__)


if __name__ == '__main__':
    subscriber_thread = threading.Thread(target=opcua_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    app.run(host='0.0.0.0', port=3000, debug=False)
