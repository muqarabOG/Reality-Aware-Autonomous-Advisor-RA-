from ..schema import PerceptionState, Entity
from typing import List

class VisualInterpreter:
    def __init__(self):
        pass

    def interpret(self, state: PerceptionState) -> str:
        """Translates perception detections into natural language."""
        if not state.entities:
            return "Clear mission area. No immediate physical obstructions detected."

        # Count entities
        counts = {}
        for ent in state.entities:
            counts[ent.label] = counts.get(ent.label, 0) + 1

        descriptions = []
        for label, count in counts.items():
            if count == 1:
                descriptions.append(f"a {label}")
            else:
                descriptions.append(f"{count} {label}s")

        # Basic spatial reasoning mock
        desc = "Scene Analysis: " + ", ".join(descriptions) + " detected in the visual field. "
        
        # Add safety context
        for ent in state.entities:
            if ent.label.lower() in ["person", "human"]:
                desc += f"WARNING: A {ent.label} is currently within the operational zone, triggering safety protocols. "
                break
        
        if state.sensor_data.get("vibration", 0) > 0.5:
            desc += "High vibration levels noted on structural sensors. "

        return desc.strip()
