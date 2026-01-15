import math

def compute_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(dy, dx))

class EarAnalysis:
    def analyze(self, left_base, left_tip, right_base, right_tip):
        result = {
            "left_angle": None,
            "right_angle": None,
            "state": "Unknown"
        }

        if left_base and left_tip:
            result["left_angle"] = compute_angle(left_base, left_tip)

        if right_base and right_tip:
            result["right_angle"] = compute_angle(right_base, right_tip)

        if result["left_angle"] is not None and result["right_angle"] is not None:
            la = result["left_angle"]
            ra = result["right_angle"]
            diff = abs(la - ra)
            avg = (la + ra) / 2

            if avg < -20:
                state = "Ears Forward (Alert/Curious)"
            elif avg > 40:
                state = "Ears Back (Fear/Submissive)"
            else:
                state = "Neutral Ears"

            if diff > 25:
                state += " + Asymmetric (Confused)"

            result["state"] = state

        return result
