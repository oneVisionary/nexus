import math

def compute_vector(p1, p2):
    return (p2[0] - p1[0], p2[1] - p1[1])

class HeadAnalysis:
    def analyze(self, nose, chin, left_eye, right_eye, throat, withers):
        result = {
            "head_up_down_angle": None,
            "head_left_right_angle": None,
            "head_tilt": None,
            "state": "Unknown"
        }

        if chin and nose:
            dx, dy = compute_vector(chin, nose)
            result["head_up_down_angle"] = math.degrees(math.atan2(dx, -dy))

        if throat and nose:
            dx, dy = compute_vector(throat, nose)
            result["head_left_right_angle"] = math.degrees(math.atan2(dy, dx))

        if left_eye and right_eye:
            dx, dy = compute_vector(left_eye, right_eye)
            result["head_tilt"] = math.degrees(math.atan2(dy, dx))

        parts = []

        up_down = result["head_up_down_angle"]
        left_right = result["head_left_right_angle"]
        tilt = result["head_tilt"]

        if up_down is not None:
            if up_down < -15:
                parts.append("Head Down (Submissive/Sad)")
            elif up_down > 15:
                parts.append("Head Up (Confident/Alert)")
            else:
                parts.append("Head Neutral")

        if left_right is not None:
            if left_right > 20:
                parts.append("Looking Right")
            elif left_right < -20:
                parts.append("Looking Left")

        if tilt is not None and abs(tilt) > 15:
            parts.append("Head Tilted (Curious)")

        if parts:
            result["state"] = " + ".join(parts)

        return result
