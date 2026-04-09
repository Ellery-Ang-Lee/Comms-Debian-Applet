import asyncio
import websockets

#if you want to modify this for encryption or something, go ahead

clients = set()
async def handler(websocket):
    clients.add(websocket)
    addr = websocket.remote_address
    print(f"Client connected: {addr} - {len(clients)} connected")
    try:
        async for message in websocket:
            print(f"Received from {addr}: {message}")
            #for client in clients - {websocket}:
            for client in clients:
                await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"Client disconnected: {addr} - {len(clients)} connected")

async def main():
    print("Starting server on 0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future() 

asyncio.run(main())