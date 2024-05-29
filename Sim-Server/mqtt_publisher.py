import paho.mqtt.client as mqtt
import random
import time
import uuid

bmws = ["BMW X7",
        "BMW M4",
        "BMW 5er Coupe",
        "BMW 3er Limousine",
        "BMW 1er Limousine",
        "BMW 7er Limousine",
        "BMW X5"]

mqttBroker = "141.56.180.177"
client = mqtt.Client(client_id="inspector")
client.connect(mqttBroker)

print("MQTT Client Connected to Broker")
while True:
        auto_id = str(uuid.uuid4()) + " " + random.choice(bmws)
        client.publish("bpa24", str(auto_id))
        print(str(auto_id) + " published to Topic AUTO_ID")
        time.sleep(2)

