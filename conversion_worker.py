import threading
import time

def start_converter_thread(queue_ref):
    def worker():
        print("🧵 Converter thread started.")
        while True:
            try:
                job = queue_ref.get()
                print("🔧 Converting:", job)
                time.sleep(2)  # Simulate conversion for now
                # TODO: Call actual conversion logic
                print("✅ Done:", job["filename"])
            except Exception as e:
                print("❌ Conversion error:", e)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
