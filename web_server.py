from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import threading
import asyncio
import queue
import html
import uvicorn
import json

app = FastAPI()
app.mount("/web-control/assets", StaticFiles(directory="web-control/assets"), name="assets")

command_queue = None  # This will be set when web server starts
matrix = None  # Shared matrix reference
lock = threading.Lock()  # Ensure thread safety when modifying the matrix

#main page
@app.get("/")
@app.get("/index.html")
async def get_index():
    try:
        with open("web-control/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: index.html not found</h1>", status_code=404)

#read program page

#read settings page

# ✅ Function to handle all button logic
async def handle_button(button_id):
    print(f"Handling button: {button_id}")

    button_actions = {
        "test1Button": test1_button_logic,
        "stopButton": handle_stop_button,
        "colorButton": change_led_color,
        "resetButton": reset_leds
    }

    # Execute the correct function
    if button_id in button_actions:
        await button_actions[button_id]()  # ✅ Call the function
    else:
        print(f"Unknown button: {button_id}")

# ✅ WebSocket handles all button clicks
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            # ✅ Handle button presses
            if "button" in data:
                button_id = data["button"]
                print(f"Button pressed: {button_id}")

                if command_queue:
                    command_queue.put(button_id)  # ✅ Add button command to queue
                    await websocket.send_json({"message": f"Button {button_id} added to queue"})
                else:
                    await websocket.send_json({"error": "Command queue not available"})

            # ✅ Handle matrix updates
            elif "matrix" in data:
                global matrix
                with lock:
                    matrix = data["matrix"]  # ✅ Store updated matrix
                print("Matrix updated via WebSocket")
                await websocket.send_json({"message": "Matrix received"})

            await asyncio.sleep(0.1)  # ✅ Prevents busy-waiting
            
    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        print("WebSocket connection closed")

async def process_commands():
    while True:
        try:
            command = command_queue.get(block=False)  # Non-blocking get
            print(f"Processing command: {command}")

            if command["command"] == "send_matrix":
                await send_matrix_to_clients()
            else:
                print(f"Unknown command: {command}")

        except queue.Empty:
            await asyncio.sleep(0.1)  # ✅ Prevents high CPU usage


def start_web_server(queue_ref): 
    global command_queue
    command_queue = queue_ref  # Assign queue reference
    #matrix = matrix_ref  # ✅ Assign shared matrix

    # Start the FastAPI server
    asyncio.run(uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info"))
