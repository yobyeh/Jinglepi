from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import html
import uvicorn

#hardcoded size of matrix in html and python

app = FastAPI()

#matrix size
columns = 16
rows = 50

matrix = [[0 for _ in range(columns)] for _ in range(rows)]
# Shared variable for LED color
current_led_color = "#000000"  # Default color

# Helper function to update a specific cell in the matrix
def update_matrix(x: int, y: int, value: int):
    global matrix
    if 0 <= x < rows and 0 <= y < columns:
        matrix[x][y] = value

# Simulate LED update (replace this with your actual LED logic)
def update_led_color(color: str):
    global current_led_color
    #current_led_color = color  # Update the shared variable
    #print(f"LED color updated to: {current_led_color}")  # Debug: Log the updated color

#read html
@app.get("/")
async def get():
    try:
        with open("index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: index.html not found</h1>", status_code=404)

#start websocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        while True:
            # Receive color data from the website
            data = await websocket.receive_text()
            print(f"Received data from WebSocket: {data}")  # Debug: Log received data
            update_led_color(data)

            # update site
            await websocket.send_json(matrix)
            await asyncio.sleep(1)  # Adjust as needed
    except Exception as e:
        print(f"WebSocket disconnected: {e}")

async def main_loop():
    global current_led_color  # Access the shared variable
    while True:
        # Read and use the current LED color
        #print(f"Main Loop: Current LED color is {current_led_color}")
        # Simulate some processing
        await asyncio.sleep(1)

if __name__ == "__main__":
    async def main():
        # Start the main loop as a background task
        asyncio.create_task(main_loop())
        # Start the FastAPI server
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    asyncio.run(main())