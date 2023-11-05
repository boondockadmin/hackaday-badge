import utime
from machine import Pin, SPI
import gc9a01

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

    # Set the foreground (text) color and background color
    foreground = 0xFFFF  # White color
    background = gc9a01.BLACK

    tft.init()
    tft.fill(background)
    utime.sleep(1)

    height = tft.height()
    width = tft.width()
    last_line = height - font.HEIGHT

    tfa = 0        # top free area
    tfb = 0        # bottom free area
    tft.vscrdef(tfa, height, tfb)

    scroll = 0

    # Split the text into words
    message = "This is a sample scrolling text. But i want a text that is much longer, and see how it shows up on the screen"
    words = message.split(' ')
    word_index = 0  # Start with the first word

    # Calculate the total height needed to scroll the complete text
    total_scroll_height = font.HEIGHT * len(words)

    while scroll < total_scroll_height:
        # clear top line before scrolling off display
        tft.fill_rect(0, scroll % height, width, font.HEIGHT, background)

        # Write a new word when we have scrolled the height of a character
        if scroll % font.HEIGHT == 0 and word_index < len(words):
            line = (scroll + last_line) % height
            current_word = words[word_index]
            text_width = font.WIDTH * len(current_word)
            start_x = (width - text_width) // 2  # Center the word

            # Display the current word
            tft.text(
                font,
                current_word,
                start_x,
                line,
                foreground,
                background)

            # Move to the next word
            word_index += 1

        # scroll the screen up 1 row
        tft.vscsad((scroll + tfa) % height)
        scroll += 1

        utime.sleep(0.01)

    # Once the complete text has scrolled, turn the screen black
    tft.fill(background)

main()
