import asyncio
import websockets
 
async def test():
    uri = "ws://localhost:8000/ws/simulation"
    print(f"Connecting to {uri} ...")
    async with websockets.connect(uri) as ws:
        message = await ws.recv()
        print("Connected. First message received:")
        print(message[:300], "..." if len(message) > 300 else "")
 
asyncio.run(test())