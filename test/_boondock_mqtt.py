import network
import time
from simple import MQTTClient
from machine import Pin, SPI
import gc9a01
import utime
import vga1_16x32 as font

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
mqtt_topic = 'boondock/5/message'

# Display setup
spi = SPI(0, baudrate=40000000, sck=Pin(2), mosi=Pin(3))
tft = gc9a01.GC9A01(
    spi,
    240,
    240,
    reset=Pin(4, Pin.OUT),
    cs=Pin(26, Pin.OUT),
    dc=Pin(5, Pin.OUT),
    backlight=Pin(27, Pin.OUT),
    rotation=0)

tft.init()
tft.fill(gc9a01.BLACK)
center_x, center_y = tft.width() // 2, tft.height() // 2

def display_centered_text(tft, text, y_offset=0):
    text_width = font.WIDTH * len(text)
    start_x = center_x - (text_width // 2)
    tft.text(font, text, start_x, center_y - (font.HEIGHT // 2) + y_offset, gc9a01.color565(255, 255, 255))
 


def print_message_smooth(msg):
    # Calculate the necessary buffer size
    text_width = font.WIDTH * len(msg)
    text_height = font.HEIGHT
    buffer_height = text_height * 2  # Double the height to have a buffer for smooth scrolling

    # Create an off-screen buffer
    buffer = gc9a01.GC9A01(
        spi,
        tft.width(),
        buffer_height,
        reset=Pin(4, Pin.OUT),
        cs=Pin(26, Pin.OUT),
        dc=Pin(5, Pin.OUT),
        rotation=0)

    # Draw the text off-screen with the message at the top and bottom
    buffer.fill(gc9a01.BLACK)
    buffer.text(font, msg, 0, 0, gc9a01.WHITE)
    buffer.text(font, msg, 0, text_height, gc9a01.WHITE)

    # Set the Vertical Scroll Definition with top and bottom fixed areas
    tft.vscrdef(0, tft.height(), 0)

    scroll = 0
    while scroll < text_height:
        # Use hardware scrolling to move the buffer up
        tft.vscsad(scroll)

        # Update the scroll position
        scroll += 1

        # Sleep for a short period to make the scroll smooth
        time.sleep(0.01)

    # Reset the scroll area after done
    tft.vscrdef(0, tft.height(), 0)
    tft.vscsad(0)

    # Clear the display after scrolling is done
    tft.fill(gc9a01.BLACK)

def print_message(msg):
    tft.fill(gc9a01.BLACK)  # Clear screen
    text_width = font.WIDTH * len(msg)
    start_x = tft.width()

    # Define the frame rate
    fps = 60
    frame_duration = 1 / fps

    while start_x + text_width > 0:  # Scroll until the entire text is off-screen to the left
        frame_start_time = utime.ticks_ms()

        tft.fill(gc9a01.BLACK)  # Clear screen for each frame of the scroll
        tft.text(font, msg, start_x, center_y - (font.HEIGHT // 2), gc9a01.color565(255, 255, 255))
        start_x -= 5  # Smaller increment for smooth scrolling

        # Update the display here if your display library supports it

        # Calculate the time spent and sleep for the remainder of the frame duration
        frame_time = utime.ticks_diff(utime.ticks_ms(), frame_start_time)
        if frame_time < frame_duration:
            time.sleep(frame_duration - frame_time)

    tft.fill(gc9a01.BLACK)  # Clear screen after scrolling is done
    display_centered_text(tft, "Waiting")
    
# Define the callback function for when a message is received
def on_message(topic, msg):
    print("Received message:", msg.decode())
    print("From topic:", topic.decode())
    print_message_smooth(msg.decode())



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
    
    # Show "Waiting" message initially
    display_centered_text(tft, "Waiting")
    
    # Proceed to connect to the MQTT server
    client = MQTTClient(client_id, mqtt_server, port=mqtt_port, user=mqtt_user, password=mqtt_password)
    client.set_callback(on_message)
    
    try:
        client.connect()
        print("Connected to MQTT Broker!")
        client.subscribe(mqtt_topic)
        print(f"Subscribed to {mqtt_topic}")

        # Wait for messages indefinitely
        while True:
            client.check_msg()
            time.sleep(1)  # A small delay to prevent CPU hogging

    except Exception as e:
        print("Failed to connect to MQTT broker. Error:", e)
else:
    print("Failed to connect to WiFi network.")

