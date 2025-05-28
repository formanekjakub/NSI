# main.py for Raspberry Pi Pico
import time
import network
import ujson
from machine import ADC, Pin
from dht import DHT11
from umqtt.simple import MQTTClient

# === Configuration ===
# Set this to the GPIO pin number where your LED is connected


# === Sensor Setup ===
soil_sensor = ADC(Pin(26))        # GP26 - Soil moisture
light_sensor = ADC(Pin(27))       # GP27 - Light sensor
dht_sensor = DHT11(Pin(22))       # GP22 - DHT11 (Temp + Humidity)


# === MQTT Configuration ===
MQTT_BROKER = '172.20.10.2'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'smart_pot_01'
MQTT_SENSOR_TOPIC = 'smartpot/sensors'
MQTT_CMD_TOPIC = 'smartpot/cmd'

# === WiFi Configuration ===
WIFI_SSID = 'Jakub-iphone'
WIFI_PASSWORD = '12345687'

# === Threshold for soil moisture alert (will be overridden via MQTT) ===
MOISTURE_THRESHOLD = 30000

# Initialize global MQTT client
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)

# === Connect to WiFi ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('WiFi connected:', wlan.ifconfig())

# === Read Sensor Functions ===
def read_soil_moisture():
    return soil_sensor.read_u16()

def read_light_level():
    return light_sensor.read_u16()

def read_temperature_and_humidity():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature(), dht_sensor.humidity()
    except Exception as e:
        print('DHT11 Error:', e)
        return None, None

# === Soil Moisture Alert Function ===
def soil_moisture_alert(threshold, on_duration=5, wait_duration=5):
    """
    If soil moisture is below threshold, turn on LED for on_duration seconds,
    then wait for wait_duration seconds, and if still below threshold, blink again.
    """
    moisture = read_soil_moisture()
    """ Future implementation of the watering (moisture control) """

# === Publish All Sensor Data ===
def publish_sensor_data(mqtt_client):
    temp, hum = read_temperature_and_humidity()
    data = {
        'client_id': MQTT_CLIENT_ID,
        'soil_moisture': read_soil_moisture(),
        'light': read_light_level(),
        'temperature': temp,
        'humidity': hum,
        'sent_time': time.time()
    }
    payload = ujson.dumps(data)
    mqtt_client.publish(MQTT_SENSOR_TOPIC, payload)

# === MQTT Callback for Incoming Commands ===
def on_mqtt_message(topic, msg):
    # Debug print of incoming raw message
    print('MQTT Msg received on topic:', topic, 'payload:', msg)
    try:
        # Decode bytes to string if necessary
        if isinstance(msg, (bytes, bytearray)):
            msg = msg.decode('utf-8')
        cmd = ujson.loads(msg)
        if 'threshold' in cmd:
            global MOISTURE_THRESHOLD
            MOISTURE_THRESHOLD = int(cmd['threshold'])
            print('Threshold updated to', MOISTURE_THRESHOLD)
    except Exception as e:
        print('Cmd parse error:', e)

# === Main Loop ===
def main():
    global client
    connect_wifi()
    client.set_callback(on_mqtt_message)
    client.connect()
    client.subscribe(MQTT_CMD_TOPIC)
    print('MQTT Connected and subscribed to', MQTT_CMD_TOPIC)

    while True:
        # Check for any incoming MQTT command updates
        try:
            client.check_msg()
        except Exception as e:
            print('MQTT check error:', e)

        # Publish sensor readings
        publish_sensor_data(client)
        # Alert on low moisture using the (possibly updated) threshold
        soil_moisture_alert(MOISTURE_THRESHOLD)
        # Wait before next cycle
        time.sleep(1)

if __name__ == '__main__':
    main()
