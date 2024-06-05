import paho.mqtt.client as mqtt
import time
from paho.mqtt.client import MQTTMessage

def mqtt_request_response(broker_address: str, port: int, request_topic: str, response_topic: str, message: str, timeout: int = 10) -> str:
    # Variable to store the response
    response_payload = None

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
        nonlocal response_payload
        print(f"Message received on topic {msg.topic}")
        response_payload = msg.payload.decode()
        print(f"Payload: {response_payload}")
        print(f"QoS: {msg.qos}")
        print(f"Retain flag: {msg.retain}")
        if msg.topic == response_topic:
            print("Response received:", response_payload)
            # Stop the loop if the response is received
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
    time.sleep(timeout)

    # Stop the loop and disconnect
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT broker")

    return response_payload

# Example usage
if __name__ == "__main__":
    broker_address = "141.56.180.177"
    port = 1883
    request_topic = "bpa24/cv/request"
    response_topic = "bpa24/cv/result"
    message = "Your message payload here"

    response = mqtt_request_response(broker_address, port, request_topic, response_topic, message)
    if response:
        print(f"Stored response: {response}")
    else:
        print("No response received")