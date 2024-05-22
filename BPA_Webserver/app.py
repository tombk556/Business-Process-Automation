from flask import Flask
import threading
import sys
from website.views import views

sys.path.append('..')
from src.utils import opcua_subscriber

app = Flask(__name__, template_folder='website/templates', static_folder='website/static')

app.register_blueprint(views, url_prefix='/')

if __name__ == '__main__':
    subscriber_thread = threading.Thread(target=opcua_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    app.run(host='0.0.0.0', port=3000, debug=True)
