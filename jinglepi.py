import threading
import queue
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from web_server import app, start_web_server, conversion_queue
from led_controller import start_led_controller
from conversion_worker import start_converter_thread
import asyncio
import uvicorn
import json
import time




#hardcoded matrix size
#data lock all shared files
#create matrix function
#persistant settings file between launches lock file file for multiple threads

lock = threading.Lock()
#shared variables
#with lock used for editing shared variables
# Shared variable for LED color

#server
# Define command queue globally
command_queue = queue.Queue()

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

            if command in button_actions:
                await asyncio.to_thread(button_actions[command])  # ✅ Runs in the main thread
            else:
                print(f"Unknown command: {command}")

        except queue.Empty:
            await asyncio.sleep(0.5)  # ✅ Prevents high CPU usage

async def main_loop():

    while True:

        print('main loop')
        # Simulate some processing
        await asyncio.sleep(5)

    pi.stop()

if __name__ == "__main__":
    async def main():

        # Start the web server in a separate thread
        web_server_thread = threading.Thread(target=start_web_server,args=(command_queue,), daemon=True)
        web_server_thread.start()

        # Start LED controller
        led_thread = threading.Thread(target=start_led_controller, args=(command_queue,), daemon=True)
        led_thread.start()

        start_converter_thread(conversion_queue)

        # Start processing commands in the main thread
        asyncio.create_task(process_commands())

        # Start the main loop as a background task
        await asyncio.create_task(main_loop())


    asyncio.run(main())