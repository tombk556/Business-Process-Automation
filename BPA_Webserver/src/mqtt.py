import paho.mqtt.client as mqtt
from config import settings
from paho.mqtt.client import MQTTMessage
import time

broker_address = settings.mqtt_url
port = int(settings.mqtt_port)

MQTT_BROKER_ADDRESS = settings.mqtt_url
MQTT_PORT = int(settings.mqtt_port)
request_topic = "bpa24/cv/request"
response_topic = "bpa24/cv/result"

def mqtt_request_response_cv(broker_address: str = MQTT_BROKER_ADDRESS, port: int = MQTT_PORT, request_topic: str = request_topic,
                          response_topic: str = response_topic, message: str = "Triggering Camera", timeout: int = 1) -> str:
    response_payload = None
    print(broker_address, port, request_topic, response_topic, message, timeout)
    def on_connect(client: mqtt.Client, userdata, flags, rc: int):
        if rc == 0:
            client.subscribe(response_topic)
        else:
            print("Connection failed with code", rc)

    def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
        nonlocal response_payload
        response_payload = msg.payload.decode()
        if msg.topic == response_topic:
            client.loop_stop()

    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address, port)

    client.loop_start()

    client.publish(request_topic, message)

    time.sleep(timeout)

    client.loop_stop()
    client.disconnect()

    return response_payload