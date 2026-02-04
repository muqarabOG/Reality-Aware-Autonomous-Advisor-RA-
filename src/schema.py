from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Entity(BaseModel):
    id: str
    label: str
    confidence: float
    bbox: Optional[List[float]] = None # [x1, y1, x2, y2]
    metadata: Dict[str, Any] = {}

class PerceptionState(BaseModel):
    timestamp: datetime
    entities: List[Entity]
    sensor_data: Dict[str, float] = {}
    anomalies_detected: bool = False

class ReasoningState(BaseModel):
    timestamp: datetime
    logic_conclusions: List[str]
    probabilistic_world_model: Dict[str, float]
    suggested_actions: List[str]
    safety_score: float
    active_alerts: List[str] = []

class ActionRecommendation(BaseModel):
    action_id: str
    description: str
    confidence: float
    parameters: Dict[str, Any] = {}

class RA3FullState(BaseModel):
    perception: PerceptionState
    reasoning: ReasoningState
    decision: ActionRecommendation
    feedback_loop_status: str
    snapshot_captured: bool = False
    current_position: List[float] = [0.0, 0.0]
    goal_position: List[float] = [10.0, 10.0]
    scene_description: str = ""
