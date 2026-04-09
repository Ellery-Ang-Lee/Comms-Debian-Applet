import asyncio
import websockets

#encryption stuff
from cryptography.fernet import Fernet
import rsa

encryption = True
server_key = Fernet.generate_key()
fernet = Fernet(server_key)
encryped_users = []
users = {}

clients = set()
async def handler(websocket):
    clients.add(websocket)
    addr = websocket.remote_address
    users[addr] = websocket
    print(f"Client connected: {addr} - {len(clients)} connected")
    try:
        async for message in websocket:
            if encryption:
                if message is rsa.PublicKey: # checks if the incoming msg is a handshake key
                    print(f"Syncing Encryption for client: {addr}")
                    await users[addr].send(rsa.encrypt(server_key, message)) #encrypts and sends server key to requesting user
                    encryped_users.append(addr)
                else:
                    print(f"Received from {addr}: {message}")
                    #for client in clients - {websocket}:
                    try:
                        encryped_users.index(addr)
                        for client in clients:
                            await client.send(message)        
                    except ValueError:
                            await users[addr].send("SERVER WARNING: You are using an unencrypted client")
                            for client in clients:
                                await client.send(fernet.encrypt(message.encode())) 
            else:
                for client in clients:
                    await client.send(message) 
                
                    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"Client disconnected: {addr} - {len(clients)} connected")

async def main():
    print("Starting server on localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future() 

asyncio.run(main())