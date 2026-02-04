from ..schema import ReasoningState, ActionRecommendation
from .pathfinding import TacticalPathfinder
from typing import List
import random
import numpy as np

class DecisionAgent:
    def __init__(self):
        self.action_history = []
        self.pathfinder = TacticalPathfinder()
        self.current_path = []

    def decide(self, reasoning: ReasoningState, current_pos: List[float], goal_pos: List[float]) -> ActionRecommendation:
        # 1. Update obstacles in pathfinder
        # In a real scenario, we'd use entity coordinates.
        # Here we'll simulate a static obstacle at [5, 5] if a CAUTION is detected.
        self.pathfinder.grid = np.zeros_like(self.pathfinder.grid) # Reset
        if any("CAUTION" in c or "ALERT" in c for c in reasoning.logic_conclusions):
             # Simulate an obstacle in the middle of a common path
             self.pathfinder.add_manual_obstacle([5.0, 5.0], radius=3.0)
             self.pathfinder.add_manual_obstacle([-5.0, -2.0], radius=2.0)

        # 2. Re-calculate path if needed
        full_path = self.pathfinder.find_path(current_pos, goal_pos)
        self.current_path = full_path
        
        # 3. Determine next waypoint (look-ahead)
        if len(self.current_path) > 2:
            # Skip the immediate next cell if we have a longer path for smoother motion
            target = self.current_path[2]
        elif len(self.current_path) > 1:
            target = self.current_path[1]
        else:
            # If no path found (likely start/end blocked), move slowly toward goal
            target = goal_pos

        dx = target[0] - current_pos[0]
        dy = target[1] - current_pos[1]
        dist = (dx**2 + dy**2)**0.5
        
        if dist > 0:
            vx, vy = dx/dist, dy/dist
        else:
            vx, vy = 0, 0
            
        # 4. Safety Modulation
        speed = 0.5
        if any("CRITICAL" in c for c in reasoning.logic_conclusions):
            return ActionRecommendation(
                action_id="STOP_EMERGENCY",
                description="A* Pathfinding halted by Critical Safety Logic.",
                confidence=1.0,
                parameters={"vx": 0, "vy": 0}
            )
            
        if any("CAUTION" in c for c in reasoning.logic_conclusions):
            speed = 0.25 # Even more caution

        # Determine description based on path state
        if not full_path:
            description = f"A* found no valid path! Attempting direct cautiously towards {goal_pos}."
            speed *= 0.5 # Slow down significantly if no path
        else:
            description = f"A* Path active. Navigating via {len(full_path)} waypoints to {goal_pos}."

        rec = ActionRecommendation(
            action_id="A_STAR_NAVIGATION",
            description=description,
            confidence=0.98,
            parameters={"vx": vx * speed, "vy": vy * speed}
        )

        self.action_history.append(rec)
        return rec
