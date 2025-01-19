import threading
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import html
import uvicorn
import json

#hardcoded size of matrix in html and python

app = FastAPI()
app.mount("/web-control/assets", StaticFiles(directory="web-control/assets"), name="assets")

#matrix size
columns = 16
rows = 50

lock = threading.Lock()
#shared variables
#with lock used for editing shared variables



#frame logic
frame_loaded = 0
frame_sent_web = 0
frame_sent_led = 0
running = 0

matrix = [[0 for _ in range(columns)] for _ in range(rows)]
# Shared variable for LED color
color_picked = "#000000"  # Default color

# Helper function to update a specific cell in the matrix
def update_Matrix(x: int, y: int, value: int):
    global matrix
    if 0 <= x < rows and 0 <= y < columns:
        matrix[x][y] = value

def solid_color_matrix(color: str):
    for x in range(columns):
        for y in range(rows):
            update_Matrix(y, x, color_picked)


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

def start_web_server():
    # Start the FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())  # Use asyncio.run to execute the async server

#read html
@app.get("/")
async def get():
    try:
        with open("web-control/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: index.html not found</h1>", status_code=404)
    
#read index
@app.get("/index.html")
async def get():
    try:
        with open("web-control/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: index.html not found</h1>", status_code=404)

#read program page

#read settings page

#start websocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        while True:
            # Receive data from the website
            message = await websocket.receive_text()
            data = json.loads(message)

            # Do something
            if "button" in data:
                button = data.get("button")

                if button == "test1Button":
                    handle_test1_button()
                    await websocket.send_text("Server: Button test1 handled")
                if button == "stopButton":
                    handle_stop_button()
                    await websocket.send_text("Server: Button stop handled")    

            else:
                print(f"Received data from WebSocket: {data}")  # Debug: Log received data
                update_color_picked(data)

                # update site
                print("Matrix before sending:", json.dumps(matrix))  # Debug: Print the full matrix
                await websocket.send_json(matrix)

            await asyncio.sleep(.1)  # Adjust as needed
    except Exception as e:
        print(f"WebSocket disconnected: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down the web server...")

async def main_loop():
    global current_led_color  # Access the shared variable
    while True:
       
        print("main loop running")

        # Simulate some processing
        await asyncio.sleep(5)

if __name__ == "__main__":
    async def main():

        # Start the web server in a separate thread
        web_server_thread = threading.Thread(target=start_web_server, daemon=True)
        web_server_thread.start()

        # Start the main loop as a background task
        await asyncio.create_task(main_loop())


    asyncio.run(main())