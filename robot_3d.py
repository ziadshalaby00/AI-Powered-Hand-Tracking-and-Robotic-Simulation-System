import websocket
import json
import time
import threading

# =========================
# Shared latest data (no queue lag)
# =========================
latest_data = None
lock = threading.Lock()

# =========================
# WebSocket Worker (background thread)
# =========================
def ws_worker():
    try:
        ws = websocket.create_connection("ws://localhost:8765")
        print("WebSocket connected ✔️")

        global latest_data

        while True:
            data_to_send = None

            # Get latest value safely
            with lock:
                data_to_send = latest_data
                latest_data = None

            if data_to_send is not None:
                try:
                    ws.send(json.dumps(data_to_send))
                except Exception as e:
                    print("WebSocket send error:", e)

            time.sleep(0.001)  # small sleep to prevent CPU 100%

    except Exception as e:
        print("WebSocket connection error:", e)


# =========================
# Start WebSocket Thread
# =========================
threading.Thread(target=ws_worker, daemon=True).start()


# =========================
# Send function (call from MediaPipe loop)
# =========================
def send_hand_data(hand_x, hand_y, last_time, fps=30):
    global latest_data

    current_time = time.time()

    # FPS control
    if current_time - last_time < 1 / fps:
        return last_time

    with lock:
        latest_data = {
            "hand_x": float(hand_x),
            "hand_y": float(hand_y)
        }

    return current_time