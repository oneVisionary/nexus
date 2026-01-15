import math

def vector(p1, p2):
    return (p2[0] - p1[0], p2[1] - p1[1])

def angle_deg(dx, dy):
    return math.degrees(math.atan2(dy, dx))

class PostureAnalysis:
    def __init__(self):
        self.prev_withers_y = None

    def analyze(self, withers, rear_knee):
        result = {
            "spine_angle": None,
            "withers_delta": None,
            "state": "Unknown"
        }

        if withers and rear_knee:
            dx, dy = vector(withers, rear_knee)
            spine_angle = angle_deg(dx, dy)
            result["spine_angle"] = spine_angle

            if self.prev_withers_y is not None:
                delta = withers[1] - self.prev_withers_y
                result["withers_delta"] = delta
            self.prev_withers_y = withers[1]

            parts = []

            if result["withers_delta"] is not None:
                if result["withers_delta"] > 8:
                    parts.append("Crouching (Fear/Submissive)")
                elif result["withers_delta"] < -8:
                    parts.append("Standing Tall (Confident)")

            if abs(spine_angle) > 50:
                parts.append("Stiff Posture (Aggressive/Alert)")
            elif abs(spine_angle) < 20:
                parts.append("Relaxed Posture (Calm)")

            if parts:
                result["state"] = " + ".join(parts)

        return result

    def reset(self):
        self.prev_withers_y = None
