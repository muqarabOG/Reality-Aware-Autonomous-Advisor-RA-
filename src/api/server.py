from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import os
import traceback
from datetime import datetime
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

mode = os.getenv("RA3_MODE", "sim").strip().lower()
print(f"[SYSTEM] Starting RA3 in {mode.upper()} mode...")
agent = RA3Agent(mode=mode)

@app.get("/")
async def root():
    return {"status": "RA3 API is running", "agent_active": agent.running, "mode": mode}

class SetGoalRequest(BaseModel):
    x: float
    y: float

@app.post("/reset_safety")
async def reset_safety():
    agent.reset_safety()
    return {"status": "Safety reset triggered"}

@app.post("/set_goal")
async def set_goal(request: SetGoalRequest):
    agent.goal_pos = [request.x, request.y]
    agent.voice.speak(f"New mission coordinates received. Navigating to grid {int(request.x)}, {int(request.y)}.")
    print(f"[SYSTEM] User set new goal: {agent.goal_pos}")
    return {"status": "success", "new_goal": agent.goal_pos}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Run one simulation step
            try:
                state = await agent.run_step()
                
                # Convert to dict
                data = state.model_dump()
                
                # Robust timestamp serialization
                def serialize_dates(obj):
                    if isinstance(obj, dict):
                        return {k: serialize_dates(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [serialize_dates(i) for i in obj]
                    elif isinstance(obj, datetime):
                        return obj.isoformat()
                    return obj

                data = serialize_dates(data)
                
                await websocket.send_text(json.dumps(data))
                await asyncio.sleep(0.5) # Faster frequency
            except Exception as loop_e:
                print(f"[ERROR] Loop Error: {loop_e}")
                traceback.print_exc()
                break
    except WebSocketDisconnect:
        print("Client disconnected from telemetry")
    except Exception as e:
        print(f"Error in telemetry WS: {e}")
        traceback.print_exc()
    finally:
        # Avoid closing if already closed to prevent RuntimeError
        if websocket.client_state.name != "DISCONNECTED":
            try:
                await websocket.close()
            except:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
