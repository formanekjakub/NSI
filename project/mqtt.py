import json
import paho.mqtt.client as mqtt
from database import insert_measurement

# ==== MQTT configuration ====
# Unique identifier for this MQTT client
MQTT_CLIENT_ID = 'dashboard_publisher'
# Address of the MQTT broker to connect to
MQTT_BROKER = "172.20.10.2"
# Topic where sensor data is published
MQTT_DATA_TOPIC = "smartpot/sensors"
# Topic to send commands back to the device
MQTT_CMD_TOPIC = "smartpot/cmd"

# Standard MQTT port and keepalive interval
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# Create the MQTT client instance and connect to the broker
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
# Start the network loop in a separate thread so that publish() works asynchronously
mqtt_client.loop_start()

def handle_connect(client, userdata, flags, return_code):
    """
    Callback triggered when the client successfully connects to the broker.
    Subscribes to the data topic to begin receiving sensor messages.
    """
    client.subscribe(MQTT_DATA_TOPIC, qos=1)

def handle_message(client, userdata, message):
    """
    Callback triggered when a new MQTT message is received.
    Parses the JSON payload and writes the measurement to the database.
    """
    try:
        # Decode the incoming payload into a Python dict
        data = json.loads(message.payload.decode())
        # Extract fields with safe defaults
        client_id     = data.get("client_id", "unknown")
        temperature   = data.get("temperature")
        humidity      = data.get("humidity")
        soil_moisture = data.get("soil_moisture")
        light_level   = data.get("light")
        sent_time     = data.get("sent_time")

        # Insert the new measurement record into the database
        insert_measurement(
            client_id=client_id,
            temperature=temperature,
            humidity=humidity,
            soil_moisture=soil_moisture,
            light_level=light_level,
            sent_time=sent_time
        )
    except Exception as err:
        # Log any errors encountered during message processing
        print("Error processing incoming message:", err)

def start_mqtt():
    """
    Configure the MQTT callbacks and start the client loop.
    This allows sensor messages to be handled while the main application runs.
    """
    mqtt_client.on_connect = handle_connect
    mqtt_client.on_message = handle_message
    # Ensure we are connected before starting to handle messages
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    mqtt_client.loop_start()

def publish_command(command_str):
    """
    Publish a command to the device on the command topic.
    Accepts either a JSON string or a Python object (which is serialized).
    """
    # Serialize if necessary
    payload = command_str if isinstance(command_str, str) else json.dumps(command_str)
    print(f"Publishing command to {MQTT_CMD_TOPIC}: {payload}")
    mqtt_client.publish(MQTT_CMD_TOPIC, payload, qos=1)
