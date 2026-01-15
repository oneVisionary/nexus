import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename

from services.DogHealthAnalyzer import DogHealthAnalyzer
from utils.settings import landmarks, device, model

# ===================== CONFIG =====================
app = Flask(__name__)
app.secret_key = "dogai_super_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

RESULT_FOLDER = os.path.join(BASE_DIR, "results")

ALLOWED_EXTENSIONS = {"mp4", "avi", "mov"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER

# ===================== AI ANALYZER =====================
analyzer = DogHealthAnalyzer(model=model, landmarks=landmarks, device=device)


# ===================== HELPERS =====================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ===================== ROUTES =====================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return redirect(url_for("dashboard"))

    file = request.files["video"]

    if file.filename == "":
        return redirect(url_for("dashboard"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        upload_folder = app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        video_path = os.path.join(upload_folder, filename)
        file.save(video_path)

        # ✅ CORRECT WEB URL
        video_url = url_for("static", filename=f"uploads/{filename}")

        # ================= AI PROCESS =================
        result = analyzer.analyze_video(video_path, output_dir=app.config["RESULT_FOLDER"])

        session["result"] = result
        session["video_url"] = video_url

        return redirect(url_for("result"))

    return redirect(url_for("dashboard"))

@app.route("/result")
def result():
    result = session.get("result")

    video_url = session.get("video_url")
    if not result:
        return redirect(url_for("dashboard"))

    return render_template(
        "result.html", video_url=video_url,
        behavior_profile=result["behavior_profile"],
        doctor_summary=result["doctor_summary"],
        audio_file=os.path.basename(result["audio_path"]),
        graphs={
            "tail": os.path.basename(result["graphs"]["tail"]),
            "ears": os.path.basename(result["graphs"]["ears"]),
            "head": os.path.basename(result["graphs"]["head"]),
            "posture": os.path.basename(result["graphs"]["posture"])
        }
    )

@app.route("/get_answer", methods=["POST"])
def get_answer():
    response = analyzer._common_question(request.json["question"])
    return {"answer": response}
    

@app.route("/results/<filename>")
def serve_results(filename):
    return send_from_directory(app.config["RESULT_FOLDER"], filename)


# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=True)
