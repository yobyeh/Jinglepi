from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import queue
import html
import uvicorn
import json

app = FastAPI()
app.mount("/web-control/assets", StaticFiles(directory="web-control/assets"), name="assets")

command_queue = None  # This will be set when web server starts

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
                    print ("test button")
                    await handle_test1_button()
                    await websocket.send_text("Server: Button test1 handled")
                if button == "stopButton":
                    #await handle_stop_button()
                    await websocket.send_text("Server: Button stop handled")    

            #else:
                print("else")

            await asyncio.sleep(.1)  # Adjust as needed
    except Exception as e:
        print(f"WebSocket disconnected: {e}")

@app.post("/trigger")
async def handle_test1_button():
    global command_queue
    if command_queue:
        command_queue.put("handle_test1_button")
        return {"message": "Function triggered in main thread"}
    else:
        return {"error": "Command queue not available"}

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down the web server...")
  

def start_web_server(queue_ref):
    global command_queue
    command_queue = queue_ref  # Assign queue reference

    # Start the FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())  # Use asyncio.run to execute the async server
