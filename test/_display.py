import random
from machine import Pin, SPI
import gc9a01
import math
import time

import vga1_16x32 as font

def main():
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
    
    # Define the center and safe radius
    center_x, center_y = 120, 120  # Assuming a 240x240 display
    safe_radius = 110  # Slightly less than half the display's width/height
    
    # Text parameters
    text = "This is KD9VFU calling KEWOB"
    start_x = 240  # Start off-screen to the right
    text_width = font.WIDTH * len(text)
    
    while True:
       # tft.fill(gc9a01.BLACK)  # Clear screen
        # If the text has scrolled to the left past the visible area, reset to the right
        if start_x < -text_width:
            start_x = 240
        tft.fill_rect(0, 100, 240, 50, gc9a01.BLACK)
        tft.text(font, text, start_x, center_y - (font.HEIGHT // 2), gc9a01.color565(255, 255, 255))
        
        start_x -= 2  # Move text to the left
        time.sleep(0.01)  # Delay to control scroll speed

main()
