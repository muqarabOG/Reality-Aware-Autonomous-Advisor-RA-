import random
import time
from datetime import datetime
from ..schema import PerceptionState, Entity

class RealitySimulator:
    def __init__(self):
        self.entities = [
            {"label": "human", "count": 2},
            {"label": "vehicle", "count": 5},
            {"label": "obstacle", "count": 0}
        ]
        self.sensor_ranges = {
            "temperature": (20.0, 35.0),
            "vibration": (0.0, 1.0),
            "proximity": (2.0, 50.0)
        }

    def get_latest_state(self) -> PerceptionState:
        # Simulate dynamic changes
        if random.random() > 0.8:
            self.entities[2]["count"] = 1 if random.random() > 0.5 else 0
        
        detected_entities = []
        for e in self.entities:
            for i in range(e["count"]):
                detected_entities.append(Entity(
                    id=f"{e['label']}_{i}",
                    label=e["label"],
                    confidence=random.uniform(0.8, 0.99),
                    bbox=[random.uniform(0, 100) for _ in range(4)]
                ))

        sensors = {k: random.uniform(v[0], v[1]) for k, v in self.sensor_ranges.items()}
        
        # Inject anomaly
        anomaly = sensors["vibration"] > 0.9 or self.entities[2]["count"] > 0

        return PerceptionState(
            timestamp=datetime.now(),
            entities=detected_entities,
            sensor_data=sensors,
            anomalies_detected=anomaly
        )

if __name__ == "__main__":
    sim = RealitySimulator()
    while True:
        state = sim.get_latest_state()
        print(f"[{state.timestamp}] Entities: {len(state.entities)}, Anomaly: {state.anomalies_detected}")
        time.sleep(2)
