import json
import threading
import time

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    print("[BRIDGE] ROS2 libraries not found. Running in MOCK mode.")

class RA3RosBridge:
    def __init__(self, agent_instance=None):
        self.agent = agent_instance
        self.running = False
        self.thread = None
        
        if ROS2_AVAILABLE:
            rclpy.init()
            self.node = Node('ra3_advisor_bridge')
            self.cmd_vel_pub = self.node.create_publisher(Twist, 'cmd_vel', 10)
        else:
            self.node = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._bridge_loop, daemon=True)
        self.thread.start()
        print("[BRIDGE] Hardware Bridge active.")

    def _bridge_loop(self):
        while self.running:
            if self.agent and not self.agent.paused:
                # In a real scenario, we'd get the latest action from the agent
                # For this bridge, we'll assume the agent's run_step updates the state
                pass
            
            # If ROS2 is available, we could spin the node here or use timers
            if ROS2_AVAILABLE and self.node:
                rclpy.spin_once(self.node, timeout_sec=0.1)
            
            time.sleep(0.1)

    def publish_action(self, action_params: dict):
        """Maps ActionRecommendation parameters to ROS2 Twist messages."""
        vx = action_params.get("vx", 0.0)
        vy = action_params.get("vy", 0.0)
        
        if ROS2_AVAILABLE and self.node:
            msg = Twist()
            msg.linear.x = float(vx)
            msg.linear.y = float(vy)
            msg.angular.z = 0.0 # Could be derived if needed
            self.cmd_vel_pub.publish(msg)
            # print(f"[ROS2] Published: vx={vx}, vy={vy}")
        else:
            # Mock output for terminal
            if abs(vx) > 0 or abs(vy) > 0:
                pass # Silently mock or log periodically

    def stop(self):
        self.running = False
        if ROS2_AVAILABLE:
            rclpy.shutdown()
        print("[BRIDGE] Hardware Bridge stopped.")
