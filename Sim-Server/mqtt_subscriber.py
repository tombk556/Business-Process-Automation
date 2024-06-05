import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage
import time

broker_address = "141.56.180.177"
port = 1883
request_topic = "bpa24/cv/request"
response_topic = "bpa24/cv/result"
message = "Your message payload here asdfasdf"

# Callback function when the client connects to the broker
def on_connect(client: mqtt.Client, userdata, flags, rc: int):
    if rc == 0:
        print("Connected to broker")
        # Subscribe to the response topic
        client.subscribe(response_topic)
    else:
        print("Connection failed with code", rc)

# Callback function when a message is received from the broker
def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == response_topic:
        print("Response received:", msg.payload.decode())
        # Optionally, you can stop the loop if you only need one response
        client.loop_stop()

client = mqtt.Client()

# Attach the on_connect and on_message callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, port)
print("Connected to MQTT broker")

# Start the loop to process network traffic, callbacks, and reconnecting
client.loop_start()

# Publish a message to the request topic
client.publish(request_topic, message)
print(f"Message published to topic {request_topic}")

# Wait for a response (you can adjust the sleep time as needed)
time.sleep(10)

# Stop the loop and disconnect
client.loop_stop()
client.disconnect()
print("Disconnected from MQTT broker")