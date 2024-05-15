from flask import Flask, jsonify
import threading
from utils import opcua_subscriber

app = Flask(__name__)

latest_auto_id = None

@app.route('/latest_auto_id', methods=['GET'])
def get_latest_auto_id():
    global latest_auto_id
    if latest_auto_id is not None:
        return jsonify({"auto_id": latest_auto_id})
    else:
        return jsonify({"message": "No Auto ID received yet"}), 404

if __name__ == '__main__':
    subscriber_thread = threading.Thread(target=opcua_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    app.run(host='0.0.0.0', port=8000)
