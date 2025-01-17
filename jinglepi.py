from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import html
import uvicorn


app = FastAPI()

#matrix size
colums = 10
rows = 10

matrix = [[0 for _ in range(colums)] for _ in range(rows)]
# Shared variable for LED color
current_led_color = "#000000"  # Default color

# Simulate LED update (replace this with your actual LED logic)
def update_led_color(color: str):
    global current_led_color
    current_led_color = color  # Update the shared variable
    print(f"LED color updated to: {current_led_color}")  # Debug: Log the updated color


@app.get("/")
async def get():
    try:
        with open("index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: index.html not found</h1>", status_code=404)


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
            await websocket.send_text(current_led_color)
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