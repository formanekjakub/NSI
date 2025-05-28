# main.py for Raspberry Pi Pico
import time
import network
import ujson
from machine import ADC, Pin
from dht import DHT11
from umqtt.simple import MQTTClient

# === Sensor Setup ===
soil_sensor = ADC(Pin(26))        # GP26 - Soil moisture
light_sensor = ADC(Pin(27))       # GP27 - Light sensor
dht_sensor = DHT11(Pin(22))       # GP22 - DHT11 (Temp + Humidity)

# === MQTT Configuration ===
MQTT_BROKER = '172.20.10.2'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'pico_client'
MQTT_TOPIC = 'smartpot/sensors'

# === WiFi Configuration ===
WIFI_SSID = 'Jakub-iphone'
WIFI_PASSWORD = '12345687'

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

# === Publish All Sensor Data ===
def publish_sensor_data(client):
    temp, hum = read_temperature_and_humidity()
    data = {
        'soil_moisture': read_soil_moisture(),
        'light': read_light_level(),
        'temperature': temp,
        'humidity': hum,
        'sent_time': time.time()  # Include send timestamp
    }
    payload = ujson.dumps(data)
    print('Publishing:', payload)
    client.publish(MQTT_TOPIC, payload)

# === Main Loop ===
def main():
    connect_wifi()
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print('MQTT Connected')

    while True:
        publish_sensor_data(client)
        time.sleep(10)

# === Run ===
main()
