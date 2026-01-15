import math

class TailAnalysis:
    def __init__(self):
        self.frame_ids = []
        self.tail_angles = []
        self.tail_statuses = []
        self.tail_intensity = []
        self.previous_angle = None   

    def record_tail_data(self, idx, tail_angle, tail_status, intensity):
        self.frame_ids.append(idx)
        self.tail_angles.append(tail_angle)
        self.tail_statuses.append(tail_status)
        self.tail_intensity.append(intensity)

    def tail_movement(self, TAIL_START, TAIL_END):
        TAIL_STATUS = ""
        angle = None
        intensity = None

        if TAIL_START is not None and TAIL_END is not None:
            dx = TAIL_END[0] - TAIL_START[0]
            dy = TAIL_END[1] - TAIL_START[1]
            angle = math.degrees(math.atan2(dy, dx))

            if self.previous_angle is not None:
                angle_diff = angle - self.previous_angle
                intensity = abs(angle_diff)

                if intensity > 20:
                    TAIL_STATUS = "Wagging"
                elif intensity > 5:
                    TAIL_STATUS = "Moving slightly"
                else:
                    TAIL_STATUS = "Still"
            else:
                TAIL_STATUS = "First frame"

            self.previous_angle = angle

        return TAIL_STATUS, angle, intensity

    def reset(self):
        self.previous_angle = None   

    # ================= NEW METHOD =================
    def get_clean_data(self):
        clean_frames = []
        clean_angles = []
        clean_intensity = []
        clean_statuses = []

        for f, a, i, s in zip(self.frame_ids, self.tail_angles, self.tail_intensity, self.tail_statuses):
            if i is not None:
                clean_frames.append(f)
                clean_angles.append(a)
                clean_intensity.append(i)
                clean_statuses.append(s)

        return clean_frames, clean_angles, clean_intensity, clean_statuses
    # ==============================================

    def plot_tail_behavior_3d(self):
        import plotly.graph_objects as go

        clean_frames, clean_angles, clean_intensity, clean_statuses = self.get_clean_data()

        fig = go.Figure()

        fig.add_trace(go.Scatter3d(
            x=clean_frames,
            y=clean_angles,
            z=clean_intensity,
            mode='markers',
            text=clean_statuses,
            marker=dict(
                size=5,
                color=clean_intensity,
                opacity=0.8
            )
        ))

        fig.update_layout(
            title="3D Dog Tail Behavior Analysis",
            scene=dict(
                xaxis_title="Frame (Time)",
                yaxis_title="Tail Angle (degrees)",
                zaxis_title="Tail Intensity"
            )
        )

        fig.write_html("tail_behavior_3d.html")
        print("3D behavior graph saved as tail_behavior_3d.html")
