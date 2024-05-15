from flask import Flask, jsonify
import threading
import sys
sys.path.append('..')
from src.utils import opcua_subscriber, latest_auto_id

app = Flask(__name__)

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

    # Run the Flask app
    app.run(host='0.0.0.0', port=3000, debug=True)
