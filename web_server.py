from fastapi import FastAPI, WebSocket, UploadFile, File # type: ignore
from fastapi.responses import HTMLResponse, JSONResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
import os
import threading
import asyncio
import queue
import html
import uvicorn # type: ignore
import json

app = FastAPI()
app.mount("/web-control/assets", StaticFiles(directory="web-control/assets"), name="assets")

command_queue = None  # This will be set when web server starts
matrix = None  # Shared matrix reference
lock = threading.Lock()  # Ensure thread safety when modifying the matrix

#uploading files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
#test
print("Current working directory:", os.getcwd())


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    #file type checking
    #if not file.filename.lower().endswith((".json", ".txt", ".csv")):
        #return JSONResponse(status_code=400, content={"message": "Only .json, .txt, or .csv files allowed."})

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    print(f"✅ File uploaded: {file.filename}")
    return {"message": f"File '{file.filename}' uploaded successfully!"}

@app.get("/list_uploads")
def list_uploads():
    try:
        files = os.listdir("uploaded_files")
        return [f for f in files if not f.startswith(".")]
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error listing files."})


#convering files to color maps
conversion_queue = queue.Queue()

@app.post("/convert_file")
async def convert_file(payload: dict):
    filename = payload.get("filename")
    grid_size = payload.get("grid_size")

    if not filename or not grid_size or "x" not in grid_size:
        return {"message": "❌ Invalid request."}

    try:
        rows, cols = map(int, grid_size.lower().split("x"))
    except ValueError:
        return {"message": "❌ Invalid grid size format."}

    # Ensure file exists
    source_path = os.path.join("uploaded_files", filename)
    if not os.path.exists(source_path):
        return {"message": f"❌ File not found: {filename}"}

    # Queue the job
    conversion_queue.put({
        "filename": filename,
        "path": source_path,
        "rows": rows,
        "cols": cols
    })

    return {"message": f"⏳ Conversion started for {filename} at {rows}x{cols}"}

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
@app.get("/program.html")
async def get_program():
    try:
        with open("web-control/program.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: program.html not found</h1>", status_code=404)

#read settings page
@app.get("/settings.html")
async def get_settings():
    try:
        with open("web-control/settings.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: settings.html not found</h1>", status_code=404)
    
#read updoad page
@app.get("/upload.html")
async def get_upload():
    try:
        with open("web-control/upload.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: upload.html not found</h1>", status_code=404)

# ✅ Function to handle all button logic
async def handle_button(button_id):
    print(f"Handling button: {button_id}")

    button_actions = {
        "test1Button": test1_button_logic,
        "stopButton": handle_stop_button,
        
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
