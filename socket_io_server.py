# =============================================================================
# =============================================================================
# This file is responsible for the operation of the fast API server 
# to establish a SOKCET connection so that I can send data 
# such as the number of fingers and the current action to the web 
# so that it appears and the robot can perform the specified action in real time.
# =============================================================================
# =============================================================================

import socketio
from fastapi import FastAPI
import uvicorn

# ==============
# Socket.IO Async Server Initialization
# ==============
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# ==============
# FastAPI Application Setup
# ==============
fastapi_app = FastAPI()

# ==============
# ASGI App Integration (FastAPI + Socket.IO)
# ==============
app = socketio.ASGIApp(sio, fastapi_app)

# ==============
# Global State Management
# ==============
clients_count = 0


# ==============
# Socket.IO Event Handlers
# ==============
@sio.event
async def connect(sid, environ):
    global clients_count
    clients_count += 1
    print(f"Client connected: {sid} | Total: {clients_count}")


@sio.event
async def disconnect(sid):
    global clients_count
    clients_count -= 1
    print(f"Client disconnected: {sid} | Total: {clients_count}")


@sio.event
async def hand_data(sid, data):
    # broadcast to all except sender
    await sio.emit("hand_data", data, skip_sid=sid)


# ==============
# Server Entry Point
# ==============
if __name__ == "__main__":
    print("Socket.IO server running on http://localhost:8765")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8765,
        log_level="info"
    )