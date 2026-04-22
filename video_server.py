# =============================================================================
# =============================================================================
# This file is responsible for the operation of the fastapi server 
# to stream data from it to the web, displaying frames coming from the core file.
# =============================================================================
# =============================================================================

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import time
from threading import Lock

# ==============
# FastAPI Application Initialization
# ==============
app = FastAPI()

# ==============
# Global Frame Buffer and Thread Safety
# ==============
latest_frame = None
frame_lock = Lock()


# ==============
# Frame Update Utility (Called from core.py)
# ==============
def set_frame(frame):
    """Call this from core.py"""
    global latest_frame
    with frame_lock:
        latest_frame = frame


# ==============
# MJPEG Frame Generator for Streaming
# ==============
def generate():
    global latest_frame

    while True:
        with frame_lock:
            frame = None if latest_frame is None else latest_frame.copy()

        if frame is None:
            time.sleep(0.1)
            continue

        _, buffer = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        )

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )

        time.sleep(1/20)  # 20 FPS stream cap


# ==============
# Video Streaming Endpoint
# ==============
@app.get("/video")
def video():
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )