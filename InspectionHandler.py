import threading
import time
from functools import partial
from src.MQTT_Camera import MQTTClient
from src.OPC_UA_Subscriber_RFID_Reader import OPC_UA_Subscriber
from src.utils.Logger import SingletonLogger
from src.utils.util_ass_response import create_response_plan
from src.utils.util_camera_inspection_response import get_simplified_inspection_response

logger = SingletonLogger()


class InspectionHandler:
    """
    InspectionHandler Class

    The `InspectionHandler` class is responsible for managing the inspection process, utilizing MQTT for communication with a camera system and OPC UA for subscribing to an assembly line. It integrates camera inspection responses with inspection plans to generate appropriate responses.

    Attributes:
        is_simulation (bool): Indicates if the system is in simulation mode. Defaults to True.
        opcua_subscriber (OPC_UA_Subscriber): An instance of the OPC UA subscriber for the assembly line.
        mqtt_client (MQTTClient): An instance of the MQTT client for communication with the camera system.

    Methods:
        __init__(self, is_simulation=True):
            Initializes the InspectionHandler with optional simulation mode.

        connect(self):
            Connects the MQTT client and OPC UA subscriber to their respective services.

        disconnect(self):
            Disconnects the MQTT client and OPC UA subscriber from their respective services.

        get_inspection_response(self, inspection_plan):
            Requests a camera inspection response via MQTT, processes the response, and generates an inspection response plan.

        run(self):
            Registers the inspection response callback and starts the OPC UA subscriber to handle incoming messages and trigger inspections.

        main(self):
            Manages the connection lifecycle, ensuring the system connects before running and disconnects afterward.

    Usage:
        handler = InspectionHandler()
        handler.main()
    """

    def __init__(self, is_simulation=True):
        self.runner_thread = None
        self.is_simulation = is_simulation
        self.test_connection_successful = False
        self.is_connected = False
        self.stop_event = threading.Event()
        self.opcua_subscriber = OPC_UA_Subscriber(self.is_simulation)
        self.mqtt_client = MQTTClient()

        # Erstellen eines gebundenen Callbacks, der self enthält
        bound_get_inspection_response = partial(self.get_inspection_response)

        # Callback mit gebundenem self registrieren
        self.opcua_subscriber.handler.register_callback(
            bound_get_inspection_response)

    def test_connection(self):
        self.opcua_subscriber.test_connection()
        self.mqtt_client.test_connection()
        if self.opcua_subscriber.test_connection_successful and self.mqtt_client.test_connection_successful:
            self.test_connection_successful = True
        else:
            self.test_connection_successful = False

    def connect(self):
        self.mqtt_client.connect()
        self.opcua_subscriber.connect()
        if self.opcua_subscriber.is_connected and self.mqtt_client.is_connected:
            self.is_connected = True
        else:
            self.is_connected = False
            logger.warning('InspectionHandler failed to connect!')

    def disconnect(self):
        self.is_connected = False
        self.opcua_subscriber.disconnect()
        self.mqtt_client.disconnect()

    def get_inspection_response(self, inspection_plan):
        camera_response = self.mqtt_client.request_response_cv(
            message="Triggering Camera", timeout=2)
        camera_response_simplified = get_simplified_inspection_response(
            camera_response, 0.6)
        inspection_response = create_response_plan(
            inspection_plan, camera_response_simplified)
        logger.info(f"Created Inspection Response: {inspection_response}")
        return inspection_response

    def run_loop(self):
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except Exception:
            logger.error("Error occurred while running the Application")

    def start(self):
        self.connect()
        try:
            self.runner_thread = threading.Thread(target=self.run_loop)
            self.runner_thread.start()
            return "active"
        except Exception as e:
            self.disconnect()
            self.stop_event.set()
            logger.error("Error occurred while starting to run the OPC UA subscriber thread")
            return f"failed"

    def stop(self):
        self.stop_event.set()
        if self.runner_thread and self.runner_thread.is_alive():
            self.runner_thread.join()
        self.disconnect()
        return "inactive"


if __name__ == "__main__":
    print("Drücke Enter zum um das Programm zu beenden...")
    handler = InspectionHandler(is_simulation=True)
    handler.start()
    input()
    handler.stop()
