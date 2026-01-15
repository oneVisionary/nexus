import os
from dotenv import load_dotenv
from ultralytics import YOLO
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from collections import Counter

from utils.settings import landmarks, device, video_path, model
from services.TailAnalysis import TailAnalysis
from services.EarAnalysis import EarAnalysis
from services.HeadAnalysis import HeadAnalysis
from services.PostureAnalyzer import PostureAnalysis

# ===================== CONFIG =====================
MAX_FRAMES = 100
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

# ===================== ENV =====================
load_dotenv()
NOVITA_KEY = os.getenv("NOVITA_KEY")
ELEVEN_KEY = os.getenv("ELEVAN_LAB")

llm_client = OpenAI(api_key=NOVITA_KEY, base_url="https://api.novita.ai/openai")
tts_client = ElevenLabs(api_key=ELEVEN_KEY)

# ===================== ANALYZERS =====================
tail_analyzer = TailAnalysis()
ear_analyzer = EarAnalysis()
head_analyzer = HeadAnalysis()
posture_analyzer = PostureAnalysis()

# ===================== COLLECTORS =====================
tail_states = []
ear_states = []
head_states = []
posture_states = []

print("🐕 Starting DOG HEALTH ANALYSIS...")

# ===================== YOLO =====================
results = model.predict(source=video_path, device=device, save=False, show=False)

# ===================== MAIN LOOP =====================
for idx, data in enumerate(results):

    if idx >= MAX_FRAMES:
        print(f"🛑 Stopped at frame {idx} (analysis limit)")
        break

    if data.keypoints is None or len(data.keypoints.xy) == 0:
        tail_analyzer.reset()
        posture_analyzer.reset()
        continue

    data_keypts = data.keypoints.xy[0].cpu().numpy()

    # -------- INIT --------
    TAIL_START = TAIL_END = None
    LEFT_EAR_BASE = LEFT_EAR_TIP = None
    RIGHT_EAR_BASE = RIGHT_EAR_TIP = None
    NOSE = CHIN = LEFT_EYE = RIGHT_EYE = None
    THROAT = WITHERS = None
    REAR_KNEE = None

    # -------- MAP --------
    for i, (x, y) in enumerate(data_keypts):
        point = (int(x), int(y))
        name = landmarks[i]

        if name == "tail_start": TAIL_START = point
        elif name == "tail_end": TAIL_END = point
        elif name == "left_ear_base": LEFT_EAR_BASE = point
        elif name == "left_ear_tip": LEFT_EAR_TIP = point
        elif name == "right_ear_base": RIGHT_EAR_BASE = point
        elif name == "right_ear_tip": RIGHT_EAR_TIP = point
        elif name == "nose": NOSE = point
        elif name == "chin": CHIN = point
        elif name == "left_eye": LEFT_EYE = point
        elif name == "right_eye": RIGHT_EYE = point
        elif name == "throat": THROAT = point
        elif name == "withers": WITHERS = point
        elif name in ["rear_left_knee", "rear_right_knee"]: REAR_KNEE = point

    # -------- ANALYSIS --------
    tail_status, _, _ = tail_analyzer.tail_movement(TAIL_START, TAIL_END)
    ear_result = ear_analyzer.analyze(LEFT_EAR_BASE, LEFT_EAR_TIP, RIGHT_EAR_BASE, RIGHT_EAR_TIP)
    head_result = head_analyzer.analyze(NOSE, CHIN, LEFT_EYE, RIGHT_EYE, THROAT, WITHERS)
    posture_result = posture_analyzer.analyze(WITHERS, REAR_KNEE)

    tail_states.append(tail_status)
    ear_states.append(ear_result["state"])
    head_states.append(head_result["state"])
    posture_states.append(posture_result["state"])

# ===================== SUMMARY ENGINE =====================
def most_common(lst):
    return Counter(lst).most_common(1)[0][0] if lst else "unknown"

tail_summary = most_common(tail_states)
ear_summary = most_common(ear_states)
head_summary = most_common(head_states)
posture_summary = most_common(posture_states)

behavior_profile = f"""
Tail: {tail_summary}
Ears: {ear_summary}
Head: {head_summary}
Posture: {posture_summary}
"""

print("\n📊 Behavior Profile:")
print(behavior_profile)

# ===================== AI DOCTOR SUMMARY =====================
def get_doctor_summary(profile_text):
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

    response = llm_client.chat.completions.create(
        model="deepseek/deepseek-v3.2",
        messages=[
            {"role": "system", "content": "You are an experienced veterinary doctor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=60,
        temperature=0.4
    )

    return response.choices[0].message.content.strip()

doctor_line = get_doctor_summary(behavior_profile)
print("\n🩺 AI DOCTOR SAYS →", doctor_line)

# ===================== TTS =====================
def generate_doctor_voice(text, output_path):
    audio = tts_client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
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

# ===================== GENERATE FINAL MP3 =====================
summary_audio_path = "final_dog_health_summary.mp3"
generate_doctor_voice(doctor_line, summary_audio_path)

print("\n✅ DONE! AI Doctor voice summary saved as:", summary_audio_path)
