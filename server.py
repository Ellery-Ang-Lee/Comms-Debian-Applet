import asyncio
import websockets
import ssl
import json
import time

#encryption stuff
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')
import time

#encryption stuff
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')


#its bad, cry about it
async def get_time()-> str:
    if 9 < time.gmtime().tm_sec: second = time.gmtime().tm_sec; 
    else: second = f"0{time.gmtime().tm_sec}"
    if 9 < time.gmtime().tm_min: minute = time.gmtime().tm_min; 
    else: minute = f"0{time.gmtime().tm_min}"
    if 9 < time.gmtime().tm_min: hour = time.gmtime().tm_hour; 
    else: hour = f"0{time.gmtime().tm_hour}"
    day = time.gmtime().tm_mday
    month = time.gmtime().tm_mon
    year = time.gmtime().tm_year
    return f"{hour}:{minute}:{second} UTC, {day}/{month}/{year}"
    


async def log_msg(addr, msg):
    log = open("./msgLogs.nut","a+")

    log.write(f"""{addr}: "{msg}" @{await get_time()}
""")
    log.close
    



clients = set()
async def handler(websocket):
    clients.add(websocket)
    addr = websocket.remote_address
    print(f"Client connected: {addr} - {len(clients)} connected")
    await websocket.send(json.dumps({ "user": "SERVER", "text": f"Client connected: {addr[0]} - {len(clients)} connected", "color": "lightgrey" }))
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received from {data['user']}: {data['text']}")
            await log_msg(addr, message)
            #for client in clients - {websocket}:
            for client in clients:
                await client.send(f"{addr}: {message} @{await get_time()}")
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
