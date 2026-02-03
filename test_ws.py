import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8000/ws/telemetry"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to RA3 Telemetry")
            for _ in range(3):
                msg = await websocket.recv()
                data = json.loads(msg)
                print(f"Received: {data['perception']['timestamp']} | Entities: {len(data['perception']['entities'])}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
