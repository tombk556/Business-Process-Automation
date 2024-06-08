from functools import partial
from src.MQTT_Camera import MQTTClient
from src.OPC_UA_Subscriber_AssemplyLine import OPC_UA_Subscriber
from src.utils.Logger import SingletonLogger
from src.utils.util_ass_response import get_response_plan
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
        self.is_simulation = is_simulation
        self.opcua_subscriber = OPC_UA_Subscriber(self.is_simulation)
        self.mqtt_client = MQTTClient()

    def connect(self):
        self.mqtt_client.connect()
        self.opcua_subscriber.connect()

    def disconnect(self):
        self.opcua_subscriber.disconnect()
        self.mqtt_client.disconnect()

    def get_inspection_response(self, inspection_plan):
        camera_response = self.mqtt_client.request_response_cv(
            message="Triggering Camera", timeout=2)
        camera_response_simplified = get_simplified_inspection_response(
            camera_response, 0.6)
        inspection_response = get_response_plan(
            inspection_plan, camera_response_simplified)
        logger.info(f"Inspection Response: {inspection_response}")
        return inspection_response

    def run(self):
        # Erstellen eines gebundenen Callbacks, der self enthält
        bound_get_inspection_response = partial(self.get_inspection_response)

        # Callback mit gebundenem self registrieren
        self.opcua_subscriber.handler.register_callback(
            bound_get_inspection_response)

        try:
            self.opcua_subscriber.run()
        except Exception as e:
            print(f"An exception occurred: {e}")

    def main(self):
        self.connect()
        try:
            self.run()
        finally:
            self.disconnect()


if __name__ == "__main__":
    handler = InspectionHandler()
    handler.main()
