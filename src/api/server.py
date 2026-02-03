from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from ..main import RA3Agent

app = FastAPI(title="RA3 Advisor API")

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mode = os.getenv("RA3_MODE", "sim")
agent = RA3Agent(mode=mode)

@app.get("/")
async def root():
    return {"status": "RA3 API is running", "agent_active": agent.running}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Run one simulation step
            state = await agent.run_step()
            
            # Convert to dict and handle datetime
            data = state.model_dump()
            data["perception"]["timestamp"] = data["perception"]["timestamp"].isoformat()
            data["reasoning"]["timestamp"] = data["reasoning"]["timestamp"].isoformat()
            
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1) # Frequency of updates
    except WebSocketDisconnect:
        print("Client disconnected from telemetry")
    except Exception as e:
        print(f"Error in telemetry WS: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
