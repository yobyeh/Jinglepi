import threading
import queue
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from web_server import start_web_server
import asyncio
import html
import uvicorn
import json
import time
import board
import neopixel_spi as neopixel


#hardcoded matrix size
#data lock all shared files
#create matrix function
#persistant settings file between launches

#matrix size
running = 0
runcount = 0

columns = 1
rows = 50

NUM_PIXELS = 50
PIXEL_ORDER = neopixel.GRB
COLORS = (0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF, 0x0000FF, 0xFF00FF)
DELAY = 0.2

spi = board.SPI()

pixels = neopixel.NeoPixel_SPI(spi,
                                NUM_PIXELS,
                                pixel_order=PIXEL_ORDER,
                                auto_write=False)



lock = threading.Lock()
#shared variables
#with lock used for editing shared variables
# Shared variable for LED color
color_picked = "#000000"  # Default color

#frame logic
#frame_loaded = 0
#frame_sent_web = 0
#frame_sent_led = 0
#running = 0
#frame_number = 0

#server
# Define command queue globally
command_queue = queue.Queue()
matrix = [[0 for _ in range(columns)] for _ in range(rows)]



# Helper function to update a specific cell in the matrix
def update_Matrix(x: int, y: int, value: int):
    """ Update a specific matrix cell """
    global matrix
    if 0 <= x < rows and 0 <= y < columns:
        with lock:
            matrix[x][y] = value
          
def reset_frame_check():
    global frame_number
    if frame_number == 800:
        frame_number = 0


def solid_color_matrix(color: str):
    for x in range(columns):
        for y in range(rows):
            update_Matrix(y, x, color_picked)

#def colorWipe():
#    """Wipe color across display a pixel at a time."""
#    for i in range(pixels):
#        for j in range(columns):
#            for k in range(rowsf):
#                update_Matrix(x, y, color_picked)
#                matrix_to_site(matrix)
                

#simulate LED update
def update_color_picked(color: str):
    global color_picked
    color_picked = color  # Update the shared variable
    #print(f"LED color updated to: {current_led_color}")  # Debug: Log the updated color

def wipe():
    global runcount

    if runcount == 0:
        print("wipe red")
        color_wipe(0xFF0000)  # Red
        runcount += 1
    elif runcount == 1:
        print("wipe green")
        color_wipe(0x00FF00)  # Green
        runcount += 1
    elif runcount == 2:
        print("wipe blue")
        color_wipe(0x0000FF)  # Blue
        runcount = 0
    


def color_wipe(color, delay=DELAY):
    """Move a color down the LED strip one by one."""
    pixels.fill(0)  # Turn off all LEDs
    for i in range(NUM_PIXELS):
        pixels[i] = color  # Set the current LED to the color
        pixels.show()
        time.sleep(delay)


#run matrix test animation
def handle_test1_button():
    global running
    print("test button 1 main file")

    if running == 0:
        running = 1
    else:
        running = 0

def handle_stop_button():
    global running
    print("stop button in main file")
    running = 0

async def send_websocket_message(data):
    """ Send data to the web server via WebSocket. """
    try:
        async with websocket.connect("ws://localhost:8000/ws") as websocket:
            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            print("WebSocket Response:", response)
    except Exception as e:
        print(f"WebSocket error: {e}")

async def process_commands():
    while True:
        try:
            command = command_queue.get(block=False)  # Non-blocking get
            print(f"Processing command: {command}")

            button_actions = {
                "test1Button": handle_test1_button,
                "stopButton": handle_stop_button,
                #"colorButton": change_led_color,
                #"resetButton": reset_leds,
            }

            if command in button_actions:
                await asyncio.to_thread(button_actions[command])  # ✅ Runs in the main thread
            else:
                print(f"Unknown command: {command}")

        except queue.Empty:
            await asyncio.sleep(0.1)  # ✅ Prevents high CPU usage

async def main_loop():
    global current_led_color  # Access the shared variable
    global running  # ✅ Use the global variable instead of creating a new one
    global runcount

    while True:
       
        print("main loop running")
        if running == 1:
            wipe()
        else:
            runcount = 0

        #run frame
        #run_frame()
        #reset_frame_check()


        # Simulate some processing
        await asyncio.sleep(5)

    pi.stop()

if __name__ == "__main__":
    async def main():

        # Start the web server in a separate thread
        web_server_thread = threading.Thread(target=start_web_server,args=(command_queue,), daemon=True)
        web_server_thread.start()

        # Start processing commands in the main thread
        asyncio.create_task(process_commands())

        # Start the main loop as a background task
        await asyncio.create_task(main_loop())


    asyncio.run(main())