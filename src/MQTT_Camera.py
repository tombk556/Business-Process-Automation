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
    def __init__(self, broker_address_in=broker_address, port_in=port):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.broker_address = broker_address_in
        self.port = port_in
        self.request_topic = request_topic
        self.response_topic = response_topic
        self.response_payload = None
        self.is_connected = False
        self.connection_established = threading.Event()
        self.message_received = threading.Event()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            client.subscribe(self.response_topic)
            self.is_connected = True
            self.connection_established.set()
            logger.info("Connected and subscribed to " + self.response_topic)
        else:
            logger.warning(f"Connection failed with reason code {reason_code}")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.is_connected = False
        if reason_code != 0:
            print(f"Unexpected disconnection with reason code {reason_code} and properties {properties}")
        self.connection_established.clear()

    def on_message(self, client, userdata, msg: MQTTMessage):
        if msg.topic == self.response_topic:
            try:
                self.response_payload = json.loads(msg.payload.decode())
                logger.info(f"Inspection Data from MQTT: {self.response_payload}")
            except json.JSONDecodeError:
                print("Error decoding JSON")
            self.message_received.set()

    def connect(self):
        if not self.is_connected:
            self.client.connect(self.broker_address, self.port)
            self.client.loop_start()
            self.connection_established.wait()

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

