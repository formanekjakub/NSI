import network
import time
import ntptime
import json
from umqtt.simple import MQTTClient
from machine import ADC, Pin

# Configuration constants
SSID = 'Jakub-iphone'
WIFI_PASS = '12345687'
BROKER = '127.0.0.1'
PORT = 1883
CLIENT_ID = 'pico_client'
DATA_TOPIC = 'temperature/data'
CMD_TOPIC = 'control/pico'

send_interval = 10
measuring = True
led_pin = Pin('LED', Pin.OUT)

# Wi-Fi setup

def init_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, WIFI_PASS)
    while not wlan.isconnected():
        print('Connecting WiFi...')
        time.sleep(1)
    print('WiFi:', wlan.ifconfig())

# Time sync

def synchronize_time():
    try:
        ntptime.settime()
        print('Time synced')
    except:
        print('Sync error')

# Timestamp formatting

def format_timestamp(offset_h=2):
    now = time.time() + offset_h*3600
    tm = time.localtime(now)
    ms = time.ticks_ms() % 1000
    return f"{tm[0]:04d}-{tm[1]:02d}-{tm[2]:02d} {tm[3]:02d}:{tm[4]:02d}:{tm[5]:02d}.{ms:03d}"

# Measure temperature

def measure_temp():
    sensor = ADC(4)
    volt = sensor.read_u16() * 3.3 / 65535
    return round(27 - (volt - 0.706)/0.001721, 2)

# Command processing

def process_command(cmd):
    global measuring, send_interval
    print('Cmd received:', cmd)
    if cmd == 'LED ON': led_pin.on()
    elif cmd == 'LED OFF': led_pin.off()
    elif cmd == 'MEASURE ON': measuring = True
    elif cmd == 'MEASURE OFF': measuring = False
    elif cmd.startswith('SET PERIOD '):
        try:
            val = int(cmd.split()[2])
            send_interval = max(1, val)
            print('New interval:', send_interval)
        except:
            print('Invalid period')

# MQTT callback

def mqtt_callback(topic, msg):
    process_command(msg.decode())

# Main loop

def run():
    global measuring, send_interval
    init_wifi()
    synchronize_time()

    client = MQTTClient(CLIENT_ID, BROKER, port=PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(CMD_TOPIC)
    print('MQTT ready')

    last = time.time()
    while True:
        client.check_msg()
        now = time.time()
        if now - last >= send_interval:
            if measuring:
                temp = measure_temp()
                ts = format_timestamp()
                payload = {'temperature': temp, 'timestamp_measurement': ts, 'timestamp_sent': ts}
                try:
                    client.publish(DATA_TOPIC, json.dumps(payload), qos=1)
                    print('Sent', payload)
                    last = now
                except Exception as e:
                    print('Send error:', e)
            else:
                print('Measurement paused')
        time.sleep(0.1)

if __name__ == '__main__':
    run()