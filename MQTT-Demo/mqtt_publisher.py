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

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Temperature_Inside")
client.connect(mqttBroker)


def rfid_sim_reader():
    while True:
        auto_id = str(uuid.uuid4()) + " " + random.choice(bmws)
        client.publish("AUTO_ID", str(auto_id))
        print(str(auto_id) + " published to Topic AUTO_ID")
        time.sleep(10)


if __name__ == '__main__':
    rfid_sim_reader()
