import network
import time
import ntptime
import json
import machine
from umqtt.simple import MQTTClient
from machine import ADC

WIFI_SSID = "Jakub-iphone"
WIFI_PASSWORD = "12345687"

MQTT_BROKER = "172.20.10.3"  # IP adresa serveru s MQTT brokerem
MQTT_PORT = 1883
MQTT_TOPIC = "temperature/data"
MQTT_CLIENT_ID = "pico_client"

SEND_INTERVAL = 5  # [sekundy]

# PŘIPOJENÍ K WIFI
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Připojuji k WiFi...")
        time.sleep(1)
    print("Připojeno k WiFi:", wlan.ifconfig())

# ZÍSKÁNÍ ČASU
def sync_time():
    try:
        ntptime.settime()
        print("Čas synchronizován s NTP")
    except:
        print("Nepodařilo se synchronizovat čas")

# MĚŘENÍ TEPLOTY (interní senzor)
def read_temperature():
    sensor = ADC(4)
    reading = sensor.read_u16() * 3.3 / 65535
    temperature = 27 - (reading - 0.706) / 0.001721
    return round(temperature, 2)

# ziskani presneho casu
def get_local_timestamp(offset_hours=2):
    # Získání času v sekundách
    timestamp_utc = time.time()
    timestamp_cest = timestamp_utc + offset_hours * 3600

    # Získání milisekundové části
    ms_total = time.ticks_ms()
    ms_part = ms_total % 1000  # jen poslední 3 čísla (0–999)

    # Rozložení na části
    ts = time.localtime(timestamp_cest)
    
    # Formátování včetně milisekund
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:03d}".format(
        ts[0], ts[1], ts[2],
        ts[3], ts[4], ts[5],
        ms_part
    )

# === Hlavní smyčka ===
def main():
    connect_wifi()
    sync_time()

    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("MQTT připojeno")

    while True:
        timestamp_meas_str = get_local_timestamp() #merene
        temp = read_temperature()
        timestamp_sent_str = get_local_timestamp() #poslane

        payload = {
            "temperature": temp,
            "timestamp_measurement": timestamp_meas_str,
            "timestamp_sent": timestamp_sent_str
        }

        try:
            client.publish(MQTT_TOPIC, json.dumps(payload), qos=1) # zpravu odesleme s QoS 1
            print("Odesláno:", payload)
        except Exception as e:
            print("Chyba při odesílání:", e)

        time.sleep(SEND_INTERVAL)

main()
