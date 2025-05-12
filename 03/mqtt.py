import json
import paho.mqtt.client as mqtt
from database import insert_measurement

BROKER = "172.20.10.2"         # IP adresa serveru s MQTT brokerem
TOPIC = "temperature/data"

def on_connect(client, userdata, flags, rc):
    print("---------------------------------")
    print("Připojeno k brokeru s kódem:", rc)
    print("---------------------------------")
    client.subscribe(TOPIC, qos=1) # povrzeni o doruceni

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        temperature = payload.get("temperature")
        ts_measured = payload.get("timestamp_measurement")
        ts_sent = payload.get("timestamp_sent")
        print(f"Přijato: {temperature}°C")
        insert_measurement(temperature, ts_measured, ts_sent)
    except Exception as e:
        print("Chyba při zpracování zprávy:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, 1883, 60)
    client.loop_start() #runs in different thread and does not block Flak
