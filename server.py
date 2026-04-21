import asyncio
import websockets

clients = set()

async def broadcast(message, sender):
    if clients:
        await asyncio.gather(*[client.send(message) for client in clients if client != sender])

async def handler(websocket):
    clients.add(websocket)
    print(f"Client connected. Total clients: {len(clients)}")
    
    try:
        async for message in websocket:
            await broadcast(message, websocket)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print("Client disconnected")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Broadcaster Server started on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())