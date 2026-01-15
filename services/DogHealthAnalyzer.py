import os
import json
from dotenv import load_dotenv
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from tavily import TavilyClient
from services.TailAnalysis import TailAnalysis
from services.EarAnalysis import EarAnalysis
from services.HeadAnalysis import HeadAnalysis
from services.PostureAnalyzer import PostureAnalysis


class DogHealthAnalyzer:
    def __init__(self, model, landmarks, device, max_frames=100, voice_id="JBFqnCBsd6RMkjVDRZzb"):
        self.model = model
        self.landmarks = landmarks
        self.device = device
        self.max_frames = max_frames
        self.voice_id = voice_id

        # ===== ENV =====
        load_dotenv()
        self.novita_key = os.getenv("NOVITA_KEY")
        self.eleven_key = os.getenv("ELEVAN_LAB")
        self.tavily_key = os.getenv("TAVILY")   
        self.tavily_client = TavilyClient(api_key=self.tavily_key)

        self.llm_client = OpenAI(api_key=self.novita_key, base_url="https://api.novita.ai/openai")
        self.tts_client = ElevenLabs(api_key=self.eleven_key)

        # ===== ANALYZERS =====
        self.tail_analyzer = TailAnalysis()
        self.ear_analyzer = EarAnalysis()
        self.head_analyzer = HeadAnalysis()
        self.posture_analyzer = PostureAnalysis()

    # =========================================================
    # MAIN ENTRY
    # =========================================================
    def analyze_video(self, video_path, output_dir="results"):
        print("🐕 Starting DOG HEALTH ANALYSIS...")

        os.makedirs(output_dir, exist_ok=True)

        per_frame_data = []
        state_history = {
            "tail": [],
            "ears": [],
            "head": [],
            "posture": []
        }

        results = self.model.predict(source=video_path, device=self.device, save=False, show=False)

        for idx, data in enumerate(results):

            if idx >= self.max_frames:
                print(f"🛑 Stopped at frame {idx} (analysis limit)")
                break

            frame_record = {
                "frame": idx,
                "tail": "unknown",
                "ears": "unknown",
                "head": "unknown",
                "posture": "unknown"
            }

            if data.keypoints is None or len(data.keypoints.xy) == 0:
                self.tail_analyzer.reset()
                self.posture_analyzer.reset()
                per_frame_data.append(frame_record)
                continue

            data_keypts = data.keypoints.xy[0].cpu().numpy()
            points = self._map_keypoints(data_keypts)

            # -------- ANALYSIS --------
            tail_status, _, _ = self.tail_analyzer.tail_movement(points["TAIL_START"], points["TAIL_END"])
            ear_result = self.ear_analyzer.analyze(
                points["LEFT_EAR_BASE"], points["LEFT_EAR_TIP"],
                points["RIGHT_EAR_BASE"], points["RIGHT_EAR_TIP"]
            )
            head_result = self.head_analyzer.analyze(
                points["NOSE"], points["CHIN"],
                points["LEFT_EYE"], points["RIGHT_EYE"],
                points["THROAT"], points["WITHERS"]
            )
            posture_result = self.posture_analyzer.analyze(points["WITHERS"], points["REAR_KNEE"])

            frame_record["tail"] = tail_status
            frame_record["ears"] = ear_result["state"]
            frame_record["head"] = head_result["state"]
            frame_record["posture"] = posture_result["state"]

            per_frame_data.append(frame_record)

            state_history["tail"].append(tail_status)
            state_history["ears"].append(ear_result["state"])
            state_history["head"].append(head_result["state"])
            state_history["posture"].append(posture_result["state"])

        # ===== SAVE JSON =====
        json_path = os.path.join(output_dir, "per_frame_behavior.json")
        with open(json_path, "w") as f:
            json.dump(per_frame_data, f, indent=4)

        print(f"📁 Per-frame JSON saved at: {json_path}")

        # ===== SUMMARY =====
        behavior_profile = self._build_behavior_profile(
            state_history["tail"],
            state_history["ears"],
            state_history["head"],
            state_history["posture"]
        )
        # ===== EMOTIONAL & MENTAL HEALTH ANALYSIS =====
        emotional_report = self._analyze_emotional_health(
            state_history["tail"],
            state_history["ears"],
            state_history["head"],
            state_history["posture"]
        )

        print("\n🧠 Emotional & Mental Health Report:\n", emotional_report)

        print("\n📊 Behavior Profile:\n", behavior_profile)

        # ===== LLM =====
        doctor_line = self._get_doctor_summary(behavior_profile)
        print("\n🩺 AI DOCTOR SAYS →", doctor_line)

        # ===== TTS =====
        audio_path = os.path.join(output_dir, "ai_doctor_summary.mp3")
        self._generate_doctor_voice(doctor_line, audio_path)

        print(f"🔊 Voice summary saved at: {audio_path}")

        # ===== GRAPHS =====
        graphs = self._generate_graphs(state_history, output_dir)

        return {
            "per_frame_json": json_path,
            "behavior_profile": behavior_profile,
            "doctor_summary": doctor_line,
            "emotional_report": emotional_report,
            "audio_path": audio_path,
            "graphs": graphs
        }
    def _analyze_emotional_health(self, tail_states, ear_states, head_states, posture_states):
        total = len(tail_states)
        if total == 0:
            return {}

        score = {
            "happy": 0,
            "sad": 0,
            "neutral": 0,
            "active": 0,
            "environment_stress": 0
        }

        for t, e, h, p in zip(tail_states, ear_states, head_states, posture_states):

            # -------- HAPPY --------
            if t in ["wagging_fast", "wagging"] and e == "forward" and h == "up":
                score["happy"] += 1

            # -------- SAD / STRESS --------
            if t in ["tucked", "still"] and (e == "back" or h == "down"):
                score["sad"] += 1

            # -------- NEUTRAL --------
            if t == "still" and e == "neutral" and h == "neutral":
                score["neutral"] += 1

            # -------- ACTIVITY --------
            if p in ["running", "jumping", "playing", "walking"]:
                score["active"] += 1

            # -------- ENVIRONMENT IMPACT --------
            if e == "back" or h == "down" or p == "crouching":
                score["environment_stress"] += 1

        # Convert to percentage
        result = {k: round((v / total) * 100, 2) for k, v in score.items()}

        # -------- Mental Health Score --------
        # Simple weighted formula
        mental_health = (
            result["happy"] * 1.0 +
            result["neutral"] * 0.6 -
            result["sad"] * 0.8 -
            result["environment_stress"] * 0.7
        )

        mental_health = max(0, min(100, round(mental_health, 2)))

        # -------- Worry Detection --------
        worry = "No immediate concern"
        if result["sad"] > 40 or result["environment_stress"] > 35:
            worry = "Yes, your dog may be stressed or uncomfortable"

        return {
            "happy_percent": result["happy"],
            "sad_percent": result["sad"],
            "neutral_percent": result["neutral"],
            "activity_percent": result["active"],
            "environment_impact_percent": result["environment_stress"],
            "mental_health_percent": mental_health,
            "should_worry": worry
        }

    # =========================================================
    # HELPERS
    # =========================================================
    def _common_question(self, query):
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )

            contents = []

            for item in response.get("results", []):
                title = item.get("title", "No title")
                content = item.get("content") or item.get("raw_content") or ""
                content = content[:800]  # truncate to avoid token explosion

                contents.append(f"Title: {title}\nContent: {content}")

            if not contents:
                return "No relevant internet results found."

            # Join list into clean text
            research_text = "\n\n".join(contents)

            prompt = f"""You are an experienced veterinary doctor and canine behavior expert.

    User question:
    {query}

    Based on the following internet research, answer the user's question in a clear, calm, and helpful way.

    Internet research:
    {research_text}

    Task:
    Summarize the key points, explain what this could mean for the dog, give safe practical advice, and mention when a veterinarian should be consulted.

    Rules:
    - Give some friendly recommendation too
    - One short paragraph
    - Friendly, reassuring tone
    - No medical diagnosis claims
    - No bullet points
    """

            response = self.llm_client.chat.completions.create(
                model="deepseek/deepseek-v3.2",
                messages=[
                    {"role": "system", "content": "You are an experienced veterinary doctor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.4
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"❌ Error in _common_question: {e}")
            return "No results found due to error."


    def _map_keypoints(self, data_keypts):
        points = {
            "TAIL_START": None, "TAIL_END": None,
            "LEFT_EAR_BASE": None, "LEFT_EAR_TIP": None,
            "RIGHT_EAR_BASE": None, "RIGHT_EAR_TIP": None,
            "NOSE": None, "CHIN": None,
            "LEFT_EYE": None, "RIGHT_EYE": None,
            "THROAT": None, "WITHERS": None,
            "REAR_KNEE": None
        }

        for i, (x, y) in enumerate(data_keypts):
            point = (int(x), int(y))
            name = self.landmarks[i]

            if name == "tail_start": points["TAIL_START"] = point
            elif name == "tail_end": points["TAIL_END"] = point
            elif name == "left_ear_base": points["LEFT_EAR_BASE"] = point
            elif name == "left_ear_tip": points["LEFT_EAR_TIP"] = point
            elif name == "right_ear_base": points["RIGHT_EAR_BASE"] = point
            elif name == "right_ear_tip": points["RIGHT_EAR_TIP"] = point
            elif name == "nose": points["NOSE"] = point
            elif name == "chin": points["CHIN"] = point
            elif name == "left_eye": points["LEFT_EYE"] = point
            elif name == "right_eye": points["RIGHT_EYE"] = point
            elif name == "throat": points["THROAT"] = point
            elif name == "withers": points["WITHERS"] = point
            elif name in ["rear_left_knee", "rear_right_knee"]:
                points["REAR_KNEE"] = point

        return points

    def _most_common(self, lst):
        return Counter(lst).most_common(1)[0][0] if lst else "unknown"

    def _build_behavior_profile(self, tail, ears, head, posture):
        return f"""
Tail: {self._most_common(tail)}
Ears: {self._most_common(ears)}
Head: {self._most_common(head)}
Posture: {self._most_common(posture)}
""".strip()

    # =========================================================
    # LLM
    # =========================================================
    def _get_doctor_summary(self, profile_text):
        prompt = f"""
You are a professional veterinary AI doctor.

Dog behavior analysis:
{profile_text}

Task:
Give ONE single-line summary in this format:
"As an AI vet, your dog is ..."

Rules:
- One line only
- No bullet points
- Friendly, caring tone
- Include health, activity, and recommendation
"""

        response = self.llm_client.chat.completions.create(
            model="deepseek/deepseek-v3.2",
            messages=[
                {"role": "system", "content": "You are an experienced veterinary doctor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    # =========================================================
    # TTS
    # =========================================================
    def _generate_doctor_voice(self, text, output_path):
        audio = self.tts_client.text_to_speech.convert(
            text=text,
            voice_id=self.voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.4,
                "similarity_boost": 0.6,
                "style": 0.6,
                "use_speaker_boost": True
            }
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

    # =========================================================
    # GRAPHS
    # =========================================================
    def _generate_graphs(self, state_history, output_dir):
        graphs = {}
        for key in ["tail", "ears", "head", "posture"]:
            path = self._plot_state_timeline(state_history[key], key, output_dir)
            graphs[key] = path
        return graphs

    def _plot_state_timeline(self, states, title, output_dir):
        encoded = self._encode_states(states)

        plt.figure()
        plt.plot(encoded)
        plt.title(f"{title.capitalize()} State Over Time")
        plt.xlabel("Frame")
        plt.ylabel("State Index")

        path = os.path.join(output_dir, f"{title}_timeline.png")
        plt.savefig(path)
        plt.close()

        print(f"📈 {title.capitalize()} graph saved at: {path}")
        return path

    def _encode_states(self, states):
        unique = list(set(states))
        mapping = {state: i for i, state in enumerate(unique)}
        return [mapping[s] for s in states]
