import network
import time
from simple import MQTTClient

# Network credentials
ssid = 'Supercon'
password = 'CtrlAltDelicious'

# MQTT server settings
mqtt_server = '18.224.112.252'  # Replace with your MQTT server's IP/URL
mqtt_port = 1883  # The standard port for MQTT is 1883
mqtt_user = 'webuser'  # Replace with your MQTT username if required
mqtt_password = 'Re9quvutyo8aSKQMf'  # Replace with your MQTT password if required
client_id = 'pico-w'  # This can be anything unique

# MQTT topic
mqtt_topic = 'boondock/5/alert'

# Define the callback function for when a message is received
def on_message(topic, msg):
    print("Received message:", msg.decode())
    print("From topic:", topic.decode())

# Start the WLAN module in station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to the specified WiFi network
wlan.connect(ssid, password)

# Wait for the connection to be established
while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting for connection...")
    time.sleep(1)

# Check if the Pico W is connected to the WiFi
if wlan.isconnected():
    print(f"Connected to {ssid}")
    print(wlan.ifconfig())
    
    # Proceed to connect to the MQTT server
    client = MQTTClient(client_id, mqtt_server, port=mqtt_port, user=mqtt_user, password=mqtt_password)
    client.set_callback(on_message)
    
    try:
        client.connect()
        print("Connected to MQTT Broker!")
        # Subscribe to the topic
        client.subscribe(mqtt_topic)
        print(f"Subscribed to {mqtt_topic}")

        # Wait for messages indefinitely
        while True:
            client.wait_msg()

    except Exception as e:
        print("Failed to connect to MQTT broker. Error:", e)
else:
    print("Failed to connect to WiFi network.")
