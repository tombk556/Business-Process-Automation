import json
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage
import threading

from config.env_config import settings
from src.utils.Logger import SingletonLogger

broker_address = settings.mqtt_url
port = int(settings.mqtt_port)
request_topic = "bpa24/cv/request"
response_topic = "bpa24/cv/result"

logger = SingletonLogger()


class MQTTClient:
    """
    MQTTClient Class

    The `MQTTClient` class manages communication with an MQTT broker, handling connection, messaging, and response processing for camera inspection requests and responses.

    Attributes:
        client (mqtt.Client): Instance of the MQTT client.
        broker_address (str): Address of the MQTT broker.
        port (int): Port number for the MQTT broker.
        request_topic (str): MQTT topic for sending inspection requests.
        response_topic (str): MQTT topic for receiving inspection responses.
        response_payload (dict): Stores the received response payload.
        is_connected (bool): Indicates if the client is connected to the broker.
        connection_established (threading.Event): Event to signal connection establishment.
        message_received (threading.Event): Event to signal message reception.

    Methods:
        __init__(self, broker_address_in=broker_address, port_in=port):
            Initializes the MQTTClient with broker address and port.

        on_connect(self, client, userdata, flags, reason_code, properties=None):
            Callback for MQTT connection event, subscribing to the response topic and setting connection flags.

        on_disconnect(self, client, userdata, flags, reason_code, properties):
            Callback for MQTT disconnection event, updating connection flags.

        on_message(self, client, userdata, msg: MQTTMessage):
            Callback for message reception, decoding JSON payload and setting message received flag.

        connect(self):
            Connects the MQTT client to the broker and waits for the connection to be established.

        send_request(self, message="Triggering Camera"):
            Publishes a message to the request topic to trigger the camera.

        request_response_cv(self, message="Triggering Camera", timeout=10):
            Sends a request and waits for a response within the specified timeout period.

        disconnect(self):
            Disconnects the MQTT client from the broker and stops the loop.

    Usage:
        mqtt_client = MQTTClient()
        mqtt_client.connect()
        response = mqtt_client.request_response_cv()
        mqtt_client.disconnect()
    """

    def __init__(self, broker_address_in=broker_address, port_in=port):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.broker_address = broker_address_in
        self.port = port_in
        self.request_topic = request_topic
        self.response_topic = response_topic
        self.response_payload = None
        self.test_connection_successful = False
        self.is_connected = False
        self.connection_established = threading.Event()
        self.message_received = threading.Event()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            client.subscribe(self.response_topic)
            self.connection_established.set()
        else:
            self.is_connected = False
            logger.warning(f"MQTT connection failed on topic {self.response_topic} with reason code {reason_code}")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.is_connected = False
        if reason_code != 0:
            logger.warning(f"Unexpected MQTT disconnection with reason code {reason_code} and properties {properties}")
            self.test_connection_successful = False
        self.connection_established.clear()

    def on_message(self, client, userdata, msg: MQTTMessage):
        if msg.topic == self.response_topic:
            try:
                self.response_payload = json.loads(msg.payload.decode())
                logger.info(f"Inspection Data from MQTT: {self.response_payload}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from MQTT on topic {self.response_topic}")
            self.message_received.set()

    def test_connection(self):
        if not self.is_connected:
            try:
                self.client.connect(self.broker_address, self.port)
                self.test_connection_successful = True
                self.client.disconnect()
            except Exception as e:
                logger.error("Error connecting to MQTT-Broker")
                self.is_connected = False
                self.test_connection_successful = False

    def connect(self):
        if not self.is_connected:
            self.test_connection()
            if self.test_connection_successful:
                self.client.connect(self.broker_address, self.port)
                self.is_connected = True
                logger.info(f"Connected and subscribed to MQTT-Broker on topic: {self.response_topic}")
                self.client.loop_start()
                self.connection_established.wait()
            else:
                self.is_connected = False

    def send_request(self, message="Triggering Camera"):
        self.client.publish(self.request_topic, message)
        self.message_received.clear()

    def request_response_cv(self, message="Triggering Camera", timeout=10):
        if not self.is_connected or not self.connection_established.is_set():
            self.connect()
        self.send_request(message)
        self.message_received.wait(timeout)
        return self.response_payload

    def disconnect(self):

        if self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            logger.info("Disconnected from MQTT server")
