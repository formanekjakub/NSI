import json
import paho.mqtt.client as mqtt
from database import insert_measurement

# ==== MQTT configuration ====
MQTT_BROKER = "172.20.10.2"           # IP address of the MQTT broker
MQTT_DATA_TOPIC = "smartpot/sensors"

MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# ==== MQTT client instance ====
mqtt_client = mqtt.Client(client_id="db_writer")

def handle_connect(client, userdata, flags, return_code):
    """Called when the MQTT client connects to the broker."""
    client.subscribe(MQTT_DATA_TOPIC, qos=1)  # subscribe with delivery confirmation


def handle_message(client, userdata, message):
    """Called when a new MQTT message arrives from Raspberry Pi Pico."""
    try:
        data = json.loads(message.payload.decode())

        temperature = data.get("temperature")
        humidity = data.get("humidity")
        soil_moisture = data.get("soil_moisture")
        light_level = data.get("light")
        sent_time = data.get("sent_time")

        print(f"Received Data:")
        print(f"  Temperature: {temperature}°C")
        print(f"  Humidity: {humidity}%")
        print(f"  Soil Moisture: {soil_moisture}")
        print(f"  Light Level: {light_level}")
        print(f"  Sent Time (Unix): {sent_time}")

        # Replace this with your actual DB or storage handler
        insert_measurement(
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
    """Send a control command over MQTT."""
    print(f"Publishing command: {command_str}")
    mqtt_client.publish(MQTT_CMD_TOPIC, command_str, qos=1)