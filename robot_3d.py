# =============================================================================
# =============================================================================
# This file is responsible for connecting to the socket.io 
# that I previously created so that I can send data to the web.
# =============================================================================
# =============================================================================

import socketio
import threading
import time
from queue import Queue

# ==============
# Socket.IO Client Initialization and Data Queue
# ==============
sio = socketio.Client(reconnection=True, reconnection_attempts=999999)
data_queue = Queue(maxsize=1)


# ==============
# Socket.IO Connection Event Handlers
# ==============
@sio.event
def connect():
    print("Socket.IO connected ✔️")


@sio.event
def disconnect():
    print("Socket.IO disconnected ❌")


# ==============
# Background Socket Worker Thread
# ==============
def socket_worker():
    while True:
        try:
            if not sio.connected:
                sio.connect("http://localhost:8765")

            if not data_queue.empty():
                data = data_queue.get()

                try:
                    sio.emit("hand_data", data)
                except Exception as e:
                    print("emit error:", e)

            time.sleep(0.01)

        except Exception as e:
            print("socket error:", e)
            time.sleep(2)


# ==============
# Start Socket Worker as Daemon Thread
# ==============
threading.Thread(target=socket_worker, daemon=True).start()


# ==============
# Rate-Limited Data Sending Utility
# ==============
def send_data(hand_data, last_time, fps=15):
    current_time = time.time()

    if current_time - last_time < 1 / fps:
        return last_time

    last_time = current_time

    if data_queue.full():
        try:
            data_queue.get_nowait()
        except:
            pass

    data_queue.put(hand_data)

    return current_time