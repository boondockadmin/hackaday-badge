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

def draw_scaled_text(font, text, x, y, scale, foreground, background):
    for char in text:
        char_index = ord(char) - ord(' ')
        char_bitmap = font[char_index]
        for row in range(font.HEIGHT):
            for col in range(font.WIDTH):
                pixel = char_bitmap[row] & (1 << col)
                if pixel:
                    tft.fill_rect(x + col*scale, y + row*scale, scale, scale, foreground)
                else:
                    tft.fill_rect(x + col*scale, y + row*scale, scale, scale, background)
        x += font.WIDTH * scale

def display_centered_text(tft, text, y_offset=0):
    text_width = font.WIDTH * len(text)
    start_x = center_x - (text_width // 2)
    tft.text(font, text, start_x, center_y - (font.HEIGHT // 2) + y_offset, gc9a01.color565(255, 255, 255))
 

def hscroll_text( message):
    # Set the foreground (text) color and background color
    foreground = 0xFFFF  # White color
    background = gc9a01.BLACK

    # Get display dimensions
    height = tft.height()
    width = tft.width()

    # Initialize scroll parameters
    scroll = width  # Start from the right of the display
    message_width = font.WIDTH * len(message)

    # Calculate the y position to vertically center the text
    text_y = (height - font.HEIGHT) // 2

    # Scroll the text from right to left
    while scroll + message_width > 0:
        tft.fill(background)  # Clear the display for the next frame
        # Draw the text at the current scroll position
        tft.text(font, message, scroll, text_y,  foreground, background)
        
        # Update the scroll position for the next frame
        scroll -= 5
        utime.sleep(0.01)

    utime.sleep(2.0)
    # Fill the screen with the background color after scrolling
    tft.fill(background)

def scroll_text(message):
    # Set the foreground (text) color and background color
    foreground = 0xFFFF  # White color
    background = gc9a01.BLACK

    # Get display dimensions
    height = tft.height()
    width = tft.width()
    last_line = height - font.HEIGHT
    tfa = 0
    tft.vscrdef(tfa, height, 0)

    # Initialize scroll parameters
    scroll = 0
    words = message.split(' ')
    word_index = 0
    total_scroll_height = font.HEIGHT * len(words)

    while scroll < total_scroll_height:
        if scroll % font.HEIGHT == 0 and word_index < len(words):
            line = (scroll + last_line) % height
            current_word = words[word_index]
            text_width = font.WIDTH * len(current_word)
            start_x = (width - text_width) // 2

            # Clear the line before drawing the text
            tft.fill_rect(0, line, width, font.HEIGHT, background)
            # Draw the text
            tft.text(
                font,
                current_word,
                start_x,
                line,
                foreground,
                background)

            word_index += 1

        # Perform the scrolling
        tft.vscsad((scroll + tfa) % height)
        scroll += 1
        utime.sleep(0.01)

    utime.sleep(2.0)
    # Fill the screen with the background color after scrolling
    tft.fill(background)


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
        start_x -= 2  # Smaller increment for smooth scrolling

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
    hscroll_text(msg.decode())



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
    

