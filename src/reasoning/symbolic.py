from ..schema import PerceptionState, ReasoningState
from datetime import datetime
from typing import List

class ReasoningEngine:
    def __init__(self):
        self.rules = [
            {"condition": "proximity < 5", "then": "Caution: Collision Risk"},
            {"condition": "vibration > 0.8", "then": "Warning: Mechanical Stress"},
            {"condition": "obstacle_count > 0", "then": "Notice: Path Obstructed"}
        ]

    def reason(self, perception: PerceptionState) -> ReasoningState:
        conclusions = []
        
        # Simple logical rules
        proximity = perception.sensor_data.get("proximity", 100)
        vibration = perception.sensor_data.get("vibration", 0)
        obstacle_count = len([e for e in perception.entities if e.label == "obstacle"])

        if proximity < 5:
            conclusions.append("CRITICAL: Emergency Stop Recommended")
        elif proximity < 15:
            conclusions.append("CAUTION: Reducing Speed")

        if vibration > 0.85:
            conclusions.append("ALERT: High vibration detected - Maintenance required")

        if obstacle_count > 0:
            conclusions.append(f"OBSERVATION: {obstacle_count} obstacle(s) in vision")

        if not conclusions:
            conclusions.append("STATUS: Nominal operations")

        # Mock probabilistic model
        prob_model = {
            "safety_prob": 0.99 if not perception.anomalies_detected else 0.4,
            "efficiency_prob": 0.85
        }

        return ReasoningState(
            timestamp=datetime.now(),
            logic_conclusions=conclusions,
            probabilistic_world_model=prob_model,
            suggested_actions=["STOP" if "CRITICAL" in c else "CONTINUE" for c in conclusions],
            safety_score=prob_model["safety_prob"]
        )
