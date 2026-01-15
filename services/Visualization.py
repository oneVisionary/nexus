import matplotlib.pyplot as plt

class Visualization:

    @staticmethod
    def plot_tail_angle(frame_ids, tail_angles):
        plt.figure()
        plt.plot(frame_ids, tail_angles)
        plt.xlabel("Frame")
        plt.ylabel("Tail Angle (deg)")
        plt.title("Tail Angle vs Frame")
        plt.savefig("tail_angle_vs_frame.png")
        plt.close()
        print("Saved tail_angle_vs_frame.png")

    @staticmethod
    def plot_tail_intensity(frame_ids, tail_intensity):
        plt.figure()
        plt.plot(frame_ids, tail_intensity)
        plt.xlabel("Frame")
        plt.ylabel("Tail Intensity")
        plt.title("Tail Intensity vs Frame")
        plt.savefig("tail_intensity_vs_frame.png")
        plt.close()
        print("Saved tail_intensity_vs_frame.png")

    @staticmethod
    def plot_head_up_down(frame_ids, head_up_down_angles):
        plt.figure()
        plt.plot(frame_ids, head_up_down_angles)
        plt.xlabel("Frame")
        plt.ylabel("Head Up/Down Angle")
        plt.title("Head Up/Down vs Frame")
        plt.savefig("head_up_down_vs_frame.png")
        plt.close()
        print("Saved head_up_down_vs_frame.png")

    @staticmethod
    def plot_posture_delta(frame_ids, withers_deltas):
        plt.figure()
        plt.plot(frame_ids, withers_deltas)
        plt.xlabel("Frame")
        plt.ylabel("Withers Delta")
        plt.title("Posture (Withers Movement) vs Frame")
        plt.savefig("posture_withers_delta_vs_frame.png")
        plt.close()
        print("Saved posture_withers_delta_vs_frame.png")

    @staticmethod
    def plot_emotion_timeline(frame_ids, emotions):
        plt.figure(figsize=(12, 4))
        plt.plot(frame_ids, range(len(frame_ids)))  # dummy y
        for i, emo in enumerate(emotions):
            plt.text(frame_ids[i], 0, emo, rotation=45, fontsize=8)
        plt.yticks([])
        plt.xlabel("Frame")
        plt.title("Emotion Timeline")
        plt.savefig("emotion_timeline.png")
        plt.close()
        print("Saved emotion_timeline.png")
