import asyncio
import os
from datetime import datetime
from .perception.simulator import RealitySimulator
from .perception.vision import VisionEngine
from .reasoning.symbolic import ReasoningEngine
from .decision.agent import DecisionAgent
from .schema import RA3FullState, ReasoningState, ActionRecommendation
from river import linear_model
from river import metrics
from .audio.voice import VoiceEngine
from .bridge.ros2 import RA3RosBridge
from .perception.interpreter import VisualInterpreter
from .database.history import MissionDatabase

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
        self.paused = False
        
        # Online Learning Model: Predict safety score based on sensors
        self.model = linear_model.LinearRegression()
        self.metric = metrics.MAE()
        self.learning_step = 0
        self.last_reset_time = 0
        
        # Physical State for Path B
        self.current_pos = [0.0, 0.0]
        self.goal_pos = [10.0, 10.0]
        
        # Audio Layer for Path D
        self.voice = VoiceEngine()
        self.voice.start()
        self.voice.speak("R A 3 System Online. Reality Aware Advisor is ready for mission.")
        
        self.bridge = RA3RosBridge(agent_instance=self)
        self.bridge.start()
        
        self.last_voice_alert = ""
        self.voice_alert_time = 0
        
        # Mastery Phase G
        self.interpreter = VisualInterpreter()
        
        # Mastery Phase I
        self.db = MissionDatabase()

    async def run_step(self):
        if self.paused:
            # Special 'Paused' Action
            if self.mode == "real" and self.perception_real:
                placeholder_perception = self.perception_real.get_perception_state({"temperature": 25.0, "vibration": 0.1, "proximity": 20.0})
            else:
                placeholder_perception = self.perception_sim.get_latest_state()
            paused_action = ActionRecommendation(
                action_id="IDLE_STANDBY", 
                description="System paused due to safety breach. Manual reset required.", 
                confidence=1.0,
                parameters={"safety_override": True}
            )
            return RA3FullState(
                perception=placeholder_perception,
                reasoning=ReasoningState(timestamp=datetime.now(), logic_conclusions=["SYSTEM PAUSED"], probabilistic_world_model={}, suggested_actions=[], safety_score=0, active_alerts=["MISSION PAUSED"]),
                decision=paused_action,
                feedback_loop_status="PAUSED / WAITING FOR RESET"
            )

        # SENSE
        if self.mode == "real" and self.perception_real:
            # Real sensor data (mocked for now, but vision is real)
            mock_sensors = {"temperature": 25.0, "vibration": 0.1, "proximity": 20.0}
            perception_state = self.perception_real.get_perception_state(mock_sensors)
        else:
            perception_state = self.perception_sim.get_latest_state()
            
        # REASON
        reasoning_state = self.reasoning.reason(perception_state)
        
        # ACT (Decide)
        action = self.decision.decide(reasoning_state, self.current_pos, self.goal_pos)
        
        # Physical Update (Path B)
        vx = action.parameters.get("vx", 0)
        vy = action.parameters.get("vy", 0)
        self.current_pos[0] += vx
        self.current_pos[1] += vy
        
        # Simple goal selection: if reached, move goal
        dist_to_goal = ((self.goal_pos[0] - self.current_pos[0])**2 + (self.goal_pos[1] - self.current_pos[1])**2)**0.5
        if dist_to_goal < 0.8:
            import random
            self.goal_pos = [random.uniform(-15, 15), random.uniform(-15, 15)]
            self.voice.speak(f"Objective reached. New target assigned.")
            print(f"[MISSION] Goal reached! New target: {self.goal_pos}")

        # LEARN: Update River model
        # Features: sensors, Labels: actual safety score from reasoning
        features = perception_state.sensor_data
        target = reasoning_state.safety_score
        
        self.model.learn_one(features, target)
        prediction = self.model.predict_one(features)
        self.metric.update(target, prediction)
        self.learning_step += 1

        status = f"Learning: MAE={self.metric.get():.4f} | {self.mode.upper()} MODE"
        
        # Path C: Actionable Triggers
        snapshot_taken = False
        import time
        current_time = time.time()
        
        if "CRITICAL" in "".join(reasoning_state.logic_conclusions):
            # Only auto-pause if we aren't in the 2-second reset grace period
            if current_time - self.last_reset_time > 2.0:
                if self.mode == "real" and self.perception_real:
                    self.perception_real.capture_snapshot()
                    snapshot_taken = True
                reasoning_state.active_alerts.append("CRITICAL SAFETY BREACH: MISSION PAUSED")
                self.paused = True # Auto-pause on critical error
                self._voice_alert("Critical safety breach. Mission paused.")
            else:
                reasoning_state.active_alerts.append("SAFETY GRACE PERIOD ACTIVE - CLEAR AREA")
                self._voice_alert("Safety grace period active. Please clear the mission area.")

        # Mastery Phase G: Scene Interpretation
        description = self.interpreter.interpret(perception_state)

        full_state = RA3FullState(
            perception=perception_state,
            reasoning=reasoning_state,
            decision=action,
            feedback_loop_status=status,
            snapshot_captured=snapshot_taken,
            current_position=self.current_pos.copy(),
            goal_position=self.goal_pos.copy(),
            scene_description=description
        )
        
        # Mastery Phase I: Mission Memory
        self.db.log_step(
            safety_score=reasoning_state.safety_score,
            mae=self.metric.get(),
            alerts=reasoning_state.active_alerts,
            scene_description=description,
            snapshot_path=self.perception_real.last_snapshot_path if snapshot_taken and self.perception_real else None
        )

        # Bridge to hardware
        self.bridge.publish_action(action.parameters)
        
        return full_state

    def reset_safety(self):
        import time
        self.paused = False
        self.last_reset_time = time.time()
        self.voice.speak("Safety reset successful. Mission resuming.")
        print("[SYSTEM] Safety reset triggered. Mission resuming...")

    def _voice_alert(self, message):
        """Throttle voice alerts to avoid repetition."""
        import time
        current_time = time.time()
        # Reduce throttle to 5 seconds and allow same message if enough time passed
        if message != self.last_voice_alert or (current_time - self.voice_alert_time) > 5.0:
            self.voice.speak(message)
            self.last_voice_alert = message
            self.voice_alert_time = current_time

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
