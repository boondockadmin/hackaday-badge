import random
from machine import Pin, SPI
import gc9a01

import utime
import italicc

import vga1_bold_16x32 as font
FONT_SCALE = 2


def main():
    spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
    tft = gc9a01.GC9A01(
        spi,
        240,
        240,
        reset=Pin(14, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(15, Pin.OUT),
        backlight=Pin(21, Pin.OUT),
        rotation=0)

    tft.init()
    tft.rotation(0)
    tft.fill(gc9a01.BLACK)
    utime.sleep(0.5)
    
    
    while True:
        utime.sleep(0.5)
        tft.text(font, "Boondock", 60, 50, gc9a01.WHITE)
        tft.text(font, "5", 120, 100, gc9a01.RED)
        tft.text(font, "Messages", 60, 140, gc9a01.GREEN)
 
       
main() 
