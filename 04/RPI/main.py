import network
import time
import ntptime
import json
from umqtt.simple import MQTTClient
from machine import ADC, Pin

# ==== Nastavení ====
WIFI_SSID = "Jakub-iphone"
WIFI_PASSWORD = "12345687"

MQTT_BROKER = "172.20.10.3"  # IP adresa serveru s MQTT brokerem
MQTT_PORT = 1883
MQTT_CLIENT_ID = "pico_client"
TOPIC_DATA = "temperature/data"
TOPIC_COMMAND = "control/pico"

SEND_INTERVAL = 10  # výchozí perioda měření [s]
measure_enabled = True
led = Pin("LED", Pin.OUT)

# ==== Wi-Fi připojení ====
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Připojuji k WiFi...")
        time.sleep(1)
    print("Připojeno:", wlan.ifconfig())

# ==== Čas ====
def sync_time():
    try:
        ntptime.settime()
        print("Čas synchronizován")
    except:
        print("Chyba při synchronizaci času")

def get_local_timestamp(offset_hours=2):
    t = time.time() + offset_hours * 3600
    ts = time.localtime(t)
    ms = time.ticks_ms() % 1000
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:03d}".format(
        ts[0], ts[1], ts[2], ts[3], ts[4], ts[5], ms
    )

# ==== Čtení teploty ====
def read_temperature():
    sensor = ADC(4)
    reading = sensor.read_u16() * 3.3 / 65535
    temperature = 27 - (reading - 0.706) / 0.001721
    return round(temperature, 2)

# ==== Zpracování příkazu ====
def handle_command(command):
    global measure_enabled, SEND_INTERVAL
    print("Přijatý příkaz:", command)

    if command == "LED ON":
        led.on()
    elif command == "LED OFF":
        led.off()
    elif command == "MEASURE ON":
        measure_enabled = True
    elif command == "MEASURE OFF":
        measure_enabled = False
    elif command.startswith("SET PERIOD "):
        try:
            value = int(command.split(" ")[2])
            SEND_INTERVAL = max(1, value)
            print("Nová perioda měření:", SEND_INTERVAL)
        except:
            print("Neplatná perioda")

# ==== MQTT Callback ====
def on_message(topic, msg):
    handle_command(msg.decode())

# ==== Hlavní program ====
def main():
    global measure_enabled, SEND_INTERVAL

    connect_wifi()
    sync_time()

    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_COMMAND)
    print("MQTT připojeno")

    last_sent = time.time()

    while True:
        client.check_msg()  # zpracuj příchozí příkazy

        now = time.time()
        if now - last_sent >= SEND_INTERVAL:
            if measure_enabled
                temp = read_temperature()
                timestamp = get_local_timestamp()

                payload = {
                    "temperature": temp,
                    "timestamp_measurement": timestamp,
                    "timestamp_sent": timestamp
                }

                try:
                    client.publish(TOPIC_DATA, json.dumps(payload), qos=1)
                    print("Odesláno:", payload)
                    last_sent = now
                except Exception as e:
                    print("Chyba při odeslání:", e)
        else:
            print("Měření pozastaveno – neodesílám data")
        last_sent = now 
        time.sleep(0.1)

main()
