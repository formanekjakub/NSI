import json
import paho.mqtt.client as mqtt
from database import add_record

# MQTT broker configuration
BROKER_ADDR = '172.20.10.2'
DATA_TOPIC = 'temperature/data'
CMD_TOPIC = 'control/pico'
PORT = 1883
KEEPALIVE = 60

client = mqtt.Client(client_id='db_writer')

# Callback for successful connection

def on_connect(cli, userdata, flags, rc):
    print('Connected with code', rc)
    cli.subscribe(DATA_TOPIC, qos=1)

# Callback for incoming messages

def on_message(cli, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        temp = payload.get('temperature')
        ts_meas = payload.get('timestamp_measurement')
        ts_sent = payload.get('timestamp_sent')
        print(f'Received: {temp}°C')
        add_record(temp, ts_meas, ts_sent)
    except Exception as e:
        print('Error processing message:', e)

# Initialize MQTT client asynchronously
def run_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()  # start loop before connecting
    try:
        client.connect_async(BROKER_ADDR, PORT, KEEPALIVE)
        print('Attempting async MQTT connection')
    except Exception as e:
        print('Error scheduling async connect:', e)

# Publish control commands safely
def send_command(cmd_str):
    try:
        print(f'Publishing {cmd_str}')
        client.publish(CMD_TOPIC, cmd_str, qos=1)
    except Exception as e:
        print('Publish error:', e)