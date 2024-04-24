from flask import Flask
import threading
import time

app = Flask(__name__)

class TestClass:
    def __init__(self):
        self.running = True

    def run(self):
        while self.running:
            print("TestClass läuft...")
            time.sleep(1)

    def stop(self):
        self.running = False

# Instanz der TestClass erstellen
test_object = TestClass()

# Thread für das TestClass-Objekt erstellen
test_thread = threading.Thread(target=test_object.run)

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
