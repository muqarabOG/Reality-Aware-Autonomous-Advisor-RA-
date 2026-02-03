from ..schema import ReasoningState, ActionRecommendation
import random

class DecisionAgent:
    def __init__(self):
        self.action_history = []

    def decide(self, reasoning: ReasoningState) -> ActionRecommendation:
        # Prioritize safety from reasoning
        if "STOP" in reasoning.suggested_actions:
            rec = ActionRecommendation(
                action_id="emergency_stop",
                description="Executing emergency stop due to critical safety risk.",
                confidence=reasoning.safety_score,
                parameters={"brake_intensity": 1.0}
            )
        elif reasoning.safety_score < 0.7:
             rec = ActionRecommendation(
                action_id="reduce_speed",
                description="Reducing speed to mitigate potential risks.",
                confidence=0.9,
                parameters={"speed_factor": 0.5}
            )
        else:
            rec = ActionRecommendation(
                action_id="proceed",
                description="Optimal path clear. Proceeding with mission.",
                confidence=reasoning.probabilistic_world_model.get("efficiency_prob", 0.9),
                parameters={"speed_factor": 1.0}
            )

        self.action_history.append(rec)
        return rec
