# led_controller.py

import time
import queue
import json
import board
import neopixel_spi as neopixel
from pathlib import Path

# Matrix config
ROWS_LED = 50
COLUMNS_LED = 1
matrix = [[]]

# Configuration
NUM_PIXELS = 50
PIXEL_ORDER = neopixel.RGB
DELAY = 0.05  # Default animation delay

# Initialize LED strip
spi = board.SPI()
pixels = neopixel.NeoPixel_SPI(spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False)

# Shared state
command_queue = None
running = False
runcount = 0
animation_frames = []
animation_fps = 30
current_frame_index = 0

def create_matrix():
    global matrix
    matrix = [[0 for _ in range(COLUMNS_LED)] for _ in range(ROWS_LED)]

def webconvert_column():
    return

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

def play_animation():
    global current_frame_index, animation_frames, animation_fps
    if not animation_frames:
        return

    frame = animation_frames[current_frame_index]
    for i in range(min(NUM_PIXELS, len(frame))):
        pixels[i] = frame[i]
    pixels.show()
    current_frame_index = (current_frame_index + 1) % len(animation_frames)
    time.sleep(1.0 / animation_fps)

def load_animation(filepath):
    global animation_frames, animation_fps, current_frame_index
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            animation_frames = [[int(pixel) for pixel in frame] for frame in data.get("frames", [])]
            animation_fps = data.get("fps", 30)
            current_frame_index = 0
            print(f"🎞️ Loaded animation with {len(animation_frames)} frames at {animation_fps} FPS")
    except Exception as e:
        print(f"❌ Failed to load animation: {e}")

def start_led_loop():
    global running

    while True:
        handle_led_commands()

        # Run animation if active
        if running:
            play_animation()
        else:
            time.sleep(0.1)

def handle_led_commands():
    """Processes commands from the queue and runs animations."""
    global running
    try:
        command = command_queue.get(block=False)

        if command == "test1Button":
            print("LED Controller: Starting wipe loop")
            running = True
            load_animation("converted/16x16/digitalfire_16x16.json")  # Example path

        elif command == "stopButton":
            print("LED Controller: Stopping animation")
            running = False
            pixels.fill(0)
            pixels.show()

    except queue.Empty:
        pass

def start_led_controller(queue_ref):
    """Entry point to start in a thread."""
    global command_queue
    command_queue = queue_ref
    create_matrix()
    print("🟢 LED controller started.")
    start_led_loop()
