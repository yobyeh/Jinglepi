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

#hardcoded matrix size
#data lock all shared files
#create matrix function
#persistant settings file between launches

#matrix size
columns = 16
rows = 50
pixels = 800

lock = threading.Lock()
#shared variables
#with lock used for editing shared variables
# Shared variable for LED color
color_picked = "#000000"  # Default color

#frame logic
frame_loaded = 0
frame_sent_web = 0
frame_sent_led = 0
running = 0
frame_number = 0

#server
# Define command queue globally
command_queue = queue.Queue()#create matrix
matrix = [[0 for _ in range(columns)] for _ in range(rows)]



# Helper function to update a specific cell in the matrix
def update_Matrix(x: int, y: int, value: int):
    global matrix
    if 0 <= x < rows and 0 <= y < columns:
        matrix[x][y] = value

def run_frame():
    colorWipe()
        
def reset_frame_check():
    global frame_number
    if frame_number == 800:
        frame_number = 0


def solid_color_matrix(color: str):
    for x in range(columns):
        for y in range(rows):
            update_Matrix(y, x, color_picked)

def colorWipe():
    """Wipe color across display a pixel at a time."""
    for i in range(pixels):
        for j in range(columns):
            for k in range(rowsf):
                update_Matrix(x, y, color_picked)
                matrix_to_site(matrix)
                

#simulate LED update
def update_color_picked(color: str):
    global color_picked
    color_picked = color  # Update the shared variable
    #print(f"LED color updated to: {current_led_color}")  # Debug: Log the updated color

#run matrix test animation
def handle_test1_button():
    print("test button 1")

def handle_stop_button():
    print("stop button")
    global running
    running = 0

async def process_commands():
    while True:
        try:
            command = command_queue.get(block=False)  # Non-blocking get
            if command == "handle_test1_button":
                handle_test1_button()  # Call the function in the main thread
        except queue.Empty:
            pass  # No new commands

async def main_loop():
    global current_led_color  # Access the shared variable
    global frame_number
    while True:
       
        print("main loop running")

        #run frame
        #run_frame()
        #reset_frame_check()


        # Simulate some processing
        await asyncio.sleep(5)

if __name__ == "__main__":
    async def main():

        # Start the web server in a separate thread
        web_server_thread = threading.Thread(target=start_web_server,args=(command_queue,), daemon=True)
        web_server_thread.start()

        # Start the main loop as a background task
        await asyncio.create_task(main_loop())


    asyncio.run(main())