import network
import credentials
import time
from simple import MQTTClient
from machine import Pin, SPI
import utime
import screen
import wifi

# Constants for WiFi and MQTT reconnection attempts
WIFI_RECONNECT_INTERVAL = 10  # seconds
MQTT_RECONNECT_INTERVAL = 10  # seconds

# Initialize last attempt timers
last_wifi_attempt = 0
last_mqtt_attempt = 0

def maintain_wifi_connection():
    global last_wifi_attempt
    if not network.WLAN(network.STA_IF).isconnected():
        # Only attempt to reconnect if WIFI_RECONNECT_INTERVAL has passed
        if time.time() - last_wifi_attempt > WIFI_RECONNECT_INTERVAL:
            screen.display_centered_text("Reconnecting WiFi...")
            wifi.connect_wifi()  # Your function to connect to WiFi
            last_wifi_attempt = time.time()
            screen.show_network_status()

def maintain_mqtt_connection():
    global last_mqtt_attempt
    # Check if an MQTT client object exists and is connected
    if  wifi.mqtt_connected:
        # Only attempt to reconnect if MQTT_RECONNECT_INTERVAL has passed
        if time.time() - last_mqtt_attempt > MQTT_RECONNECT_INTERVAL:
            screen.display_centered_text("Reconnecting MQTT...")
            wifi.connect_mqtt()  # Your function to connect to MQTT
            last_mqtt_attempt = time.time()

screen.display_centered_text("Init")
# Connec to Wifi
wifi.connect_wifi()
screen.display_centered_text("MQTT")
wifi.connect_mqtt()

# Show "Waiting" message initially
screen.display_centered_text("Waiting")
screen.show_network_status()

# Main loop
while True:
    maintain_wifi_connection()
    maintain_mqtt_connection()
    # Your main code logic would be here
    # Sleep for a bit to avoid a busy loop
    time.sleep(1)