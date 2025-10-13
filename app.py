import os, uuid
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

REFUSAL_TEXT = (
    "My expertise is strictly limited to agriculture. "
    "Please ask me a question about your crops, soil, market prices, or farming practices."
)

def allowed_file(fname):
    return "." in fname and fname.rsplit(".",1)[1].lower() in {"png","jpg","jpeg","webp"}

def save_image(file):
    if not file or not allowed_file(file.filename):
        raise ValueError("Invalid image format")
    name = secure_filename(file.filename)
    name = f"{os.path.splitext(name)[0]}_{uuid.uuid4().hex}{os.path.splitext(name)[1]}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], name)
    file.save(path)
    Image.open(path).verify()
    return "/static/uploads/" + name

def generate_ai_response(text):
    t = text.lower()
    agri_words = [
        "crop","soil","irrig","pest","disease","harvest","yield","market",
        "price","fertilizer","manure","weed","pesticide","seed","sowing","cultiv"
    ]
    if not any(w in t for w in agri_words):
        return {"text": REFUSAL_TEXT}

    if any(w in t for w in ["price","market","trend"]):
        return {
            "text": (
                "HERE IS A BRIEF SUMMARY: WHEAT PRICES IN RAJASTHAN SHOW A MODEST "
                "UPWARD TREND OVER 8 MONTHS, PEAKING IN NOV 2024."
            ),
            "chart": {
                "chartType": "line",
                "title": "HISTORICAL PRICE OF WHEAT (RAJASTHAN)",
                "unit": "RS/QUINTAL",
                "data": [
                    {"label":"2024-05","value":2200},
                    {"label":"2024-07","value":2250},
                    {"label":"2024-09","value":2320},
                    {"label":"2024-11","value":2400},
                    {"label":"2025-01","value":2350},
                ]
            },
            "sources": [{"title":"LOCAL SAMPLE DATA","uri":"#"}]
        }

    if "pest" in t or "worm" in t:
        return {"text": "Spray NEEM OIL (5–10 ml/L) and use pheromone traps to control pests."}

    if "soil" in t or "fertil" in t:
        return {"text": "Test soil pH. Add compost or lime/sulphur based on test results."}

    if "irrig" in t or "water" in t:
        return {"text": "Use DRIP IRRIGATION and mulch to reduce evaporation losses."}

    return {"text": "Provide crop name and issue for more specific agricultural guidance."}

@app.route("/")
def home(): return render_template("index.html")

@app.route("/upload_image", methods=["POST"])
def upload_image():
    f = request.files.get("image")
    try:
        path = save_image(f)
        return jsonify({"path": path})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/submit_query", methods=["POST"])
def submit_query():
    data = request.get_json(force=True)
    text = data.get("text","").strip()
    if not text: return jsonify({"error":"Empty query"}),400
    result = generate_ai_response(text)
    return jsonify(result)

@app.route("/static/uploads/<path:fname>")
def get_upload(fname):
    return send_from_directory(app.config["UPLOAD_FOLDER"], fname)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
