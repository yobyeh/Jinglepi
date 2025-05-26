import os
import json
import threading
import queue
from PIL import Image, ImageSequence
from pathlib import Path

FPS = 30  # Target FPS for all conversions


def ensure_output_folder(rows, cols):
    path = Path(f"converted/{rows}x{cols}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def rgb_to_hex_int(r, g, b):
    return (r << 16) | (g << 8) | b


def remap_snaked_vertical(frame, rows, cols):
    """Convert 2D pixel data to 1D list based on zigzag wiring."""
    mapped = []
    for col in range(cols):
        column = [frame.getpixel((col, row)) for row in range(rows)]
        if col % 2 == 0:
            column = list(reversed(column))  # Bottom to top
        for r, g, b in column:
            mapped.append(rgb_to_hex_int(r, g, b))
    return mapped

def convert_gif_to_matrix(filepath, rows, cols):
    im = Image.open(filepath)
    im = im.convert("RGB")

    duration_ms = im.info.get("duration", 100)
    frame_interval_ms = 1000 / FPS

    frames = []
    last_time = 0
    frame_time = 0

    for frame in ImageSequence.Iterator(im):
        if frame_time >= last_time:
            resized = frame.convert("RGB").resize((cols, rows))
            mapped = remap_snaked_vertical(resized, rows, cols)
            frames.append(mapped)
            last_time += frame_interval_ms

        frame_time += duration_ms

    return {
        "rows": rows,
        "cols": cols,
        "fps": FPS,
        "frames": frames
    }


def save_converted_animation(data, original_name, rows, cols):
    out_folder = ensure_output_folder(rows, cols)
    base_name = Path(original_name).stem
    out_path = out_folder / f"{base_name}_{rows}x{cols}.json"
    with open(out_path, "w") as f:
        json.dump(data, f)
    print(f"✅ Saved: {out_path}")


def start_converter_thread(queue_ref):
    def worker():
        print("🧵 Conversion thread running...")
        while True:
            try:
                job = queue_ref.get()
                filename = job["filename"]
                path = job["path"]
                rows = job["rows"]
                cols = job["cols"]

                print(f"🔄 Converting {filename} to {rows}x{cols}...")
                result = convert_gif_to_matrix(path, rows, cols)
                save_converted_animation(result, filename, rows, cols)

            except Exception as e:
                print(f"❌ Conversion failed: {e}")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
