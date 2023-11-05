import network
import credentials
import time
from simple import MQTTClient
import screen

wifi_connected = 0
mqtt_connected = 0


# Define the callback function for when a message is received
def on_message(topic, msg):
    print("Received message:", msg.decode())
    print("From topic:", topic.decode())
    screen.hscroll_text(msg.decode())

def on_connect():
    print("MQTT Conencted")
    mqtt_connected = 1
    
def on_disconnect():
    print("MQTT Disconnected")
    mqtt_connected = 0

    # Start the WLAN module in station mode
wlan = network.WLAN(network.STA_IF)
mqttClient = MQTTClient(credentials.client_id, credentials.mqtt_server, port=credentials.mqtt_port, user=credentials.mqtt_user, password=credentials.mqtt_password)
mqttClient.set_callback(on_message)
mqttClient.on_connect = on_connect()
mqttClient.on_disconnect = on_disconnect()


def connect_mqtt():
    if wlan.isconnected():
        # Proceed to connect to the MQTT server
        try:
            mqttClient.connect()
            print("Connected to MQTT Broker!")
            screen.display_centered_text("MQTT OK")
            mqttClient.subscribe(credentials.mqtt_topic)
            print(f"Subscribed to {credentials.mqtt_topic}")
            screen.display_centered_text("SUB OK")
            mqtt_connected = 1

            # Wait for messages indefinitely
            while True:
                mqttClient.check_msg()
                time.sleep(1)  # A small delay to prevent CPU hogging

        except Exception as e:
            print("Failed to connect to MQTT broker. Error:", e)
            screen.display_centered_text("MQTT Fail")

def connect_wifi():
    wlan.active(True)
    screen.display_centered_text("WIFI...")
    # Connect to the specified WiFi network
    wlan.connect(credentials.ssid, credentials.password)

    # Wait for the connection to be established
    while not wlan.isconnected() and wlan.status() >= 0:
        print("Waiting for connection...")
        time.sleep(1)

    # Check if the Pico W is connected to the WiFi
    if wlan.isconnected():
        wifi_connected = 1
        print(f"Connected to {credentials.ssid}")
        screen.display_centered_text("WIFI OK")

    else:
        print("Failed to connect to WiFi network.")
        screen.display_centered_text("WiFi ERR")