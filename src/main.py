import asyncio
import os
from datetime import datetime
from .perception.simulator import RealitySimulator
from .perception.vision import VisionEngine
from .reasoning.symbolic import ReasoningEngine
from .decision.agent import DecisionAgent
from .schema import RA3FullState
from river import linear_model
from river import metrics

class RA3Agent:
    def __init__(self, mode="sim"):
        self.mode = mode
        self.perception_sim = RealitySimulator()
        self.perception_real = VisionEngine() if mode == "real" else None
        
        if self.perception_real:
            self.perception_real.start()
            
        self.reasoning = ReasoningEngine()
        self.decision = DecisionAgent()
        self.running = False
        
        # Online Learning Model: Predict safety score based on sensors
        self.model = linear_model.LinearRegression()
        self.metric = metrics.MAE()
        self.learning_step = 0

    async def run_step(self):
        # SENSE
        if self.mode == "real":
            # Real sensor data (mocked for now, but vision is real)
            mock_sensors = {"temperature": 25.0, "vibration": 0.1, "proximity": 20.0}
            perception_state = self.perception_real.get_perception_state(mock_sensors)
        else:
            perception_state = self.perception_sim.get_latest_state()
        
        # REASON
        reasoning_state = self.reasoning.reason(perception_state)
        
        # ACT (Decide)
        action = self.decision.decide(reasoning_state)
        
        # LEARN: Update River model
        # Features: sensors, Labels: actual safety score from reasoning
        features = perception_state.sensor_data
        target = reasoning_state.safety_score
        
        self.model.learn_one(features, target)
        prediction = self.model.predict_one(features)
        self.metric.update(target, prediction)
        self.learning_step += 1

        status = f"Learning: MAE={self.metric.get():.4f} | Steps={self.learning_step}"

        full_state = RA3FullState(
            perception=perception_state,
            reasoning=reasoning_state,
            decision=action,
            feedback_loop_status=status
        )
        
        return full_state

    async def start(self):
        self.running = True
        print("RA3 Agent Started.")
        while self.running:
            state = await self.run_step()
            print(f"[{state.perception.timestamp}] Action: {state.decision.action_id} | Safety: {state.reasoning.safety_score}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    agent = RA3Agent()
    asyncio.run(agent.start())
