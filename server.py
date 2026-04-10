import asyncio
import websockets
import ssl
import json
import time

#encryption stuff
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

#its good now, be happy
async def get_time()-> str:
    return time.strftime("%H:%M:%S UTC, %d/%m/%Y", time.gmtime())
    
async def log_msg(msg):
    entry = json.loads(msg)
    entry["time"] = await get_time()
    with open("./msgLogs.jsonl", "a") as log:
        log.write(json.dumps(entry) + "\n")

clients = set()
async def handler(websocket):
    clients.add(websocket)
    addr = websocket.remote_address
    print(f"Client connected: {addr} - {len(clients)} connected")
    for client in clients:
        await client.send(json.dumps({ "user": "SERVER", "text": f"Client connected: {addr[0]} - {len(clients)} connected", "color": "lightgrey" }))
    
     try:
         with open("./msgLogs.jsonl", "r") as log:
             for line in log.readlines()[-10:]:
                 if line.strip():
                     await websocket.send(line.strip())
     except Exception as e:
         print(f"Error reading log file: {e}")

    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received from {data['user']}: {data['text']}")
            await log_msg(message)
            for client in clients:
                #await client.send(f"{addr}: {message} @{await get_time()}")
                await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"Client disconnected: {addr[0]} - {len(clients)} connected")
        for client in clients:  # everyone except the one that left
            await client.send(json.dumps({ "user": "SERVER", "text": f"Client disconnected: {addr[0]} - {len(clients)} connected", "color": "grey" }))

async def main():
    print("Starting server on 0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765, ssl=ssl_context):
        await serverInput()
        await asyncio.Future() 

async def serverInput():
    loop = asyncio.get_event_loop()
    while True:
        text = await loop.run_in_executor(None, input)  # runs input() in a thread
        msg = json.dumps({ "user": "SERVER", "text": text, "color": "lightgrey" })
        for client in clients:
            await client.send(msg)

asyncio.run(main())
