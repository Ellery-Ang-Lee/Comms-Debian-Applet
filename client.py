import asyncio
import websockets
import argparse


#encryption stuff
from cryptography.fernet import Fernet
import rsa

#client cli because i dont want to use js
#i dont feel link figuring out the websocket stuff nor the async stuff rn 
#so please make thing send and run

public_key, private_key = rsa.newkeys(512) #handshake encryption

server_key: bytes
fernet: Fernet


#this needs to connect
async def join(server_ip, username = "anon"):
    server = f"ws://{server_ip}:8765"
    try:
        async with websockets.connect(server) as websocket:
            await websocket.send(public_key)
            server_key = rsa.decrypt(await websocket.recv(), private_key)
            fernet = Fernet(server_key)
            while not websockets.ConnectionClosed:
                #accepts incoming msgs
                output = websocket.recv()
                if output != "":
                    print(fernet.decrypt(output).decode) #decrypts incoming msg
                output = ""
                #sends msgs
                user_input = f"{username}: {input(">")}"
                await websocket.send(fernet.encrypt(user_input.encode)) #encrypts outgoing msg
                
            
    except websockets.exceptions.ConnectionClosed:
        print(f"""Failed to connect to {server} 
              -> check IP or internet connection""")





async def main():
    parser = argparse.ArgumentParser(
        description="Connect to encrypted websocket for messaging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bcom "192.0.16.4" "User123"
        """,
    )
    parser.add_argument(
        "ip", type=str, default="0.0.0.0", help="The server host's IP adress",
    )
    parser.add_argument(
        "username", type=str, default="anon", help="Your username",
    )

    args = parser.parse_args()
    await join(args.ip, args.username)



main()