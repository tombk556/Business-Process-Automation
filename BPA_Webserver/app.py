from flask import Flask, render_template
import threading
import sys

sys.path.append("..")
from src.utils import opcua_subscriber

app = Flask(__name__, template_folder="website/templates", static_folder="website/static")


@app.route("/")
def view_logs():
    with open("app.log", "r") as file:
        logs = file.read()
    return render_template("logs.html", logs=logs)

if __name__ == "__main__":
    subscriber_thread = threading.Thread(target=opcua_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    app.run(host="0.0.0.0", port=3000, debug=False)
