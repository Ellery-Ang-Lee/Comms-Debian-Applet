import asyncio
import websockets
import ssl

#encryption stuff
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

clients = set()
async def handler(websocket):
    clients.add(websocket)
    addr = websocket.remote_address
    print(f"Client connected: {addr} - {len(clients)} connected")
    await websocket.send(f"Client connected: {addr[0]} - {len(clients)} connected")
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
        print(f"Client disconnected: {addr[0]} - {len(clients)} connected")
        for client in clients:  # everyone except the one that left
            await client.send(f"Client disconnected: {addr} - {len(clients)} connected")

async def main():
    print("Starting server on 0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765, ssl=ssl_context):
        await asyncio.Future() 

asyncio.run(main())