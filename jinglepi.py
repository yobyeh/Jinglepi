from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import html
import uvicorn

# Simulate LED update (replace this with your actual LED logic)
def update_led_color(color: str):
    print(f"LED Color updated to: {color}")
    # Here, add the logic to change your LEDs to the given color

app = FastAPI()

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

if __name__ == "__main__":
    # Start the Uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=8000)