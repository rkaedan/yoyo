import streamlit as st
import os
import uuid
from PIL import Image
import matplotlib.pyplot as plt

# --- CONFIG ---
st.set_page_config(page_title="Krishi-Sahayak Offline", layout="wide")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

REFUSAL_TEXT = (
    "My expertise is strictly limited to agriculture. "
    "Please ask me a question about your crops, soil, market prices, or farming practices."
)

# --- HELPER FUNCTIONS ---

def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])

def save_image(image_file):
    if image_file is None:
        return None
    if not allowed_file(image_file.name):
        st.error("❌ Invalid file type. Upload JPG, PNG, or WEBP only.")
        return None
    unique_name = f"{uuid.uuid4().hex}_{image_file.name}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    img = Image.open(image_file)
    img.save(path)
    return path

def generate_response(text):
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
                "title": "Historical Wheat Prices (Rajasthan)",
                "unit": "₹/Quintal",
                "data": [
                    ("2024-05", 2200),
                    ("2024-07", 2250),
                    ("2024-09", 2320),
                    ("2024-11", 2400),
                    ("2025-01", 2350),
                ],
            }
        }

    if "pest" in t or "worm" in t:
        return {"text": "Spray NEEM OIL (5–10 ml/L) and use pheromone traps to control pests."}

    if "soil" in t or "fertil" in t:
        return {"text": "Test soil pH. Add compost or lime/sulphur based on test results."}

    if "irrig" in t or "water" in t:
        return {"text": "Use DRIP IRRIGATION and mulch to reduce evaporation losses."}

    return {"text": "Provide crop name and issue for more specific agricultural guidance."}

# --- UI ---
st.title("🌾 Krishi-Sahayak : Cybernetic Data Terminal (Offline Mode)")
st.markdown("#### A simple offline AI assistant for farmers")

# Sidebar
st.sidebar.header("📂 Upload Section")
uploaded_img = st.sidebar.file_uploader("Upload a crop image (optional)", type=["jpg","jpeg","png","webp"])
if uploaded_img:
    img_path = save_image(uploaded_img)
    if img_path:
        st.sidebar.image(img_path, caption="Uploaded Image", use_container_width=True)

# Query input
query = st.text_area("💬 Enter your question or query here:", height=100, placeholder="e.g., What is the best fertilizer for wheat?")
submit = st.button("🚀 Submit Query")

# Chat logic
if submit and query.strip():
    result = generate_response(query)

    st.markdown("### 🤖 Krishi-Sahayak Response:")
    st.success(result["text"])

    if "chart" in result:
        chart = result["chart"]
        labels = [x[0] for x in chart["data"]]
        values = [x[1] for x in chart["data"]]

        fig, ax = plt.subplots()
        ax.plot(labels, values, marker="o")
        ax.set_title(chart["title"])
        ax.set_ylabel(chart["unit"])
        ax.set_xlabel("Month")
        st.pyplot(fig)

elif submit and not query.strip():
    st.warning("⚠️ Please type a query first.")

# Footer
st.markdown("---")
st.caption("Developed for offline agricultural assistance • No AI API or Internet required.")

