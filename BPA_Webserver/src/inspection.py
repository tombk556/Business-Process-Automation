import paho.mqtt.client as mqtt


def publish_inspection_plan(inspection_plan):
    """
        publish inspection plan to MQTT broker to the topic inspection_plan
    """
    
    mqttBroker = "mqtt.eclipseprojects.io"
    client = mqtt.Client("Temperature_Inside")
    client.connect(mqttBroker)
    
    client.publish("inspection_plan", str(inspection_plan))