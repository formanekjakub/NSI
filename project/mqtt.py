import json
import paho.mqtt.client as mqtt
from database import insert_measurement

# ==== MQTT configuration ====
MQTT_CLIENT_ID = 'dashboard_publisher'
MQTT_BROKER = "172.20.10.2"           # IP address of the MQTT broker
MQTT_DATA_TOPIC = "smartpot/sensors"
MQTT_CMD_TOPIC = "smartpot/cmd"  

MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# Create & connect your publisher client
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
# Start the network loop in its own thread so publishes actually go out:
mqtt_client.loop_start()

def handle_connect(client, userdata, flags, return_code):
    """Called when the MQTT client connects to the broker."""
    client.subscribe(MQTT_DATA_TOPIC, qos=1)  # subscribe with delivery confirmation


def handle_message(client, userdata, message):
    """Called when a new MQTT message arrives from Raspberry Pi Pico."""
    try:
        data = json.loads(message.payload.decode())
        client_id     = data.get("client_id", "unknown")
        temperature   = data.get("temperature")
        humidity      = data.get("humidity")
        soil_moisture = data.get("soil_moisture")
        light_level   = data.get("light")
        sent_time     = data.get("sent_time")

        insert_measurement(
            client_id=client_id,           # ← now required
            temperature=temperature,
            humidity=humidity,
            soil_moisture=soil_moisture,
            light_level=light_level,
            sent_time=sent_time
    )

    except Exception as err:
        print("Error processing incoming message:", err)

def start_mqtt():
    """
    Initialize and start the MQTT client loop in a background thread.
    This allows the Flask app (or other main loop) to continue running.
    """
    mqtt_client.on_connect = handle_connect
    mqtt_client.on_message = handle_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    mqtt_client.loop_start()

def publish_command(command_str):
    # If you passed in a dict/json-able, make it a string:
    payload = command_str if isinstance(command_str, str) else json.dumps(command_str)
    print(f"Publishing command to {MQTT_CMD_TOPIC}: {payload}")
    mqtt_client.publish(MQTT_CMD_TOPIC, payload, qos=1)

