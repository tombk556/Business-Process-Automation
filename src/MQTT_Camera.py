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
    Manages communication with an MQTT broker, specifically for handling connection, messaging,
    and response processing related to camera inspection requests and results.

    This class facilitates the publishing of inspection requests and the handling of asynchronous
    responses from an MQTT broker, employing events to manage the synchronous aspects of asynchronous 
    communications.

    Attributes:
        client (mqtt.Client): Instance of the MQTT client using MQTT v5.0 protocol.
        broker_address (str): Address of the MQTT broker.
        port (int): Port number to connect to the MQTT broker.
        request_topic (str): MQTT topic for publishing inspection requests.
        response_topic (str): MQTT topic for subscribing to receive inspection responses.
        response_payload (dict): Stores the latest received response payload.
        is_connected (bool): True if the client is successfully connected to the broker.
        connection_established (threading.Event): An event to signal successful connection establishment.
        message_received (threading.Event): An event to signal the receipt of a new message.

    Methods:
        __init__(self, broker_address_in, port_in):
            Initializes the MQTTClient with specified broker address and port. Defaults are provided
            through module-level configuration.

        on_connect(self, client, userdata, flags, reason_code, properties=None):
            Handles successful connection events, subscribes to the response topic, and signals readiness.

        on_disconnect(self, client, userdata, reason_code, properties):
            Handles the disconnection event, resets connection flags, and logs the event.

        on_message(self, client, userdata, msg):
            Processes received messages, decodes JSON payloads, and logs the data.

        test_connection(self):
            Attempts to connect to the MQTT broker to check the connection status.

        connect(self):
            Establishes a connection with the MQTT broker and begins the network loop.

        send_request(self, message):
            Publishes a request message to the specified request topic.

        request_response_cv(self, message, timeout):
            Sends a request for camera inspection and waits for a response within the specified timeout.

        disconnect(self):
            Stops the network loop and disconnects from the MQTT broker.

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
