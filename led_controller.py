# led_controller.py

import time
import queue
import board
import neopixel_spi as neopixel

# Configuration
NUM_PIXELS = 50
PIXEL_ORDER = neopixel.RGB
DELAY = 0.05  # Speed of animations

# Initialize LED strip
spi = board.SPI()
pixels = neopixel.NeoPixel_SPI(spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False)

# Shared state
command_queue = None
running = False
runcount = 0

def color_wipe(color, delay=DELAY):
    """Wipe a color down the strip one LED at a time."""
    pixels.fill(0)
    for i in range(NUM_PIXELS):
        pixels[i] = color
        pixels.show()
        time.sleep(delay)

def wipe_cycle():
    """Cycle through 3 basic colors."""
    global runcount
    if runcount == 0:
        print("Running RED wipe")
        color_wipe(0xFF0000)
    elif runcount == 1:
        print("Running GREEN wipe")
        color_wipe(0x00FF00)
    elif runcount == 2:
        print("Running BLUE wipe")
        color_wipe(0x0000FF)
    
    runcount = (runcount + 1) % 3

def handle_led_commands():
    """Processes commands from the queue and runs animations."""
    global running

    while True:
        try:
            # Check for new commands
            command = command_queue.get(block=False)

            if command == "test1Button":
                print("LED Controller: Starting wipe loop")
                running = True

            elif command == "stopButton":
                print("LED Controller: Stopping animation")
                running = False
                pixels.fill(0)
                pixels.show()

        except queue.Empty:
            pass

        # Run animation if active
        if running:
            wipe_cycle()
        else:
            time.sleep(0.1)

def start_led_controller(queue_ref):
    """Entry point to start in a thread."""
    global command_queue
    command_queue = queue_ref
    print("🟢 LED controller started.")
    handle_led_commands()
