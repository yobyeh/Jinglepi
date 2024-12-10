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
    print(f"LED Color updated to: {color}")
    # Here, add the logic to change your LEDs to the given color


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
    try:
        while True:
            # Receive color data from the website
            data = await websocket.receive_text()
            update_led_color(data)
    except Exception as e:
        print(f"WebSocket disconnected: {e}")

async def main_loop():
    global current_led_color  # Access the shared variable
    while True:
        # Read and use the current LED color
        print(f"Main Loop: Current LED color is {current_led_color}")
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