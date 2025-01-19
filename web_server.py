from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import html
import uvicorn
import json

app = FastAPI()
app.mount("/web-control/assets", StaticFiles(directory="web-control/assets"), name="assets")

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

def start_web_server():
    # Start the FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())  # Use asyncio.run to execute the async server
