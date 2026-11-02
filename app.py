import os
import requests
import streamlit as st
import pandas as pd
import joblib
from groq import Groq

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="FitFinder | AI Fashion Stylist",
    page_icon="👕",
    layout="wide"
)

# ==========================================
# 2. PERMANENT THEME (MONOCHROMATIC)
# ==========================================
bg_color = "#FFB989"       # Pink/Peach background
text_color = "#691313"     # Very dark maroon for text
card_bg = "#FFDC9C"        # Lightest peach for cards
accent = "#C12B2B"         # Strong red for accents
btn_bg = "#691313"         # Dark maroon for buttons
btn_text = "#FFFFFF"       # White text on buttons
sidebar_bg = "#FFDC9C"     # Light peach sidebar

# ==========================================
# 3. CSS STYLING
# ==========================================
st.markdown(f"""
<style>
.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}
h1, h2, h3, p, span, div {{
    color: {text_color} !important;
}}
[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
}}
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] div {{
    color: {text_color} !important;
}}
div[data-testid="stChatInput"] textarea {{
    color: {text_color} !important;
    background-color: {card_bg} !important;
}}
div[data-testid="stChatMessage"] {{
    background-color: {card_bg};
    border: 1px solid {accent};
    border-radius: 15px;
    padding: 12px;
}}
.result-card {{
    background-color: {card_bg};
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid {accent};
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}}
.result-label {{
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: {accent} !important;
    margin-bottom: 5px;
}}
.result-text {{
    font-size: 28px;
    font-weight: bold;
    margin-top: 0;
}}
.stButton>button {{
    background-color: {btn_bg} !important;
    color: {btn_text} !important;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: bold;
}}
.stButton>button:hover {{
    opacity: 0.8;
    color: {btn_text} !important;
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR (IMAGE & INFO)
# ==========================================
with st.sidebar:
    try:
        st.image("indian_art.jpeg", use_container_width=True)
    except Exception:
        st.warning("Image not found in folder.")
        
    st.divider()
    st.markdown("## 👕 FitFinder")
    st.caption("AI-Powered Fashion Assistant")
    st.divider()
    st.markdown("### About")
    st.write("FitFinder uses Machine Learning to predict body types and recommend clothing sizes.")
    st.divider()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("FitFinder © 2026")

# ==========================================
# 5. HEADER
# ==========================================
st.markdown('<h1 style="text-align: center;">FitFinder 👕</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 18px;">Discover Your Perfect Fit. Define Your Style.</p>', unsafe_allow_html=True)

# ==========================================
# 6. LOAD ML MODELS
# ==========================================
@st.cache_resource
def load_models():
    bodytype_pipeline = joblib.load("models/bodytype_pipeline.pkl")
    bodytype_labels = joblib.load("models/bodytype_labels.pkl")
    size_model = joblib.load("models/size_category_model.pkl")
    size_columns = joblib.load("models/model_columns.pkl")
    return bodytype_pipeline, bodytype_labels, size_model, size_columns

try:
    bodytype_pipeline, bodytype_labels, size_model, size_columns = load_models()
except Exception as e:
    st.error(f"Model loading error: {e}")
    st.stop()

# ==========================================
# 7. GROQ CLIENT
# ==========================================
@st.cache_resource
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key:
        return None
    return Groq(api_key=api_key)

# ==========================================
# 8. UNSPLASH IMAGES
# ==========================================
@st.cache_data(show_spinner=False)
def get_unsplash_images(body_type, gender, search_query=None, count=10):
    access_key = st.secrets.get("UNSPLASH_ACCESS_KEY")
    if not access_key: return []
        
    gender_term = "men" if gender == "Male" else "women" if gender == "Female" else "fashion"
        
    if search_query:
        query = f"{gender_term} {search_query}"
    else:
        body_term = body_type.lower()
        if "broad" in body_term or "heavy" in body_term:
            style_term = "oversized tailored streetwear"
        elif "petite" in body_term:
            style_term = "high waisted aesthetic"
        elif "slim" in body_term:
            style_term = "layered minimalist fashion"
        else:
            style_term = "classic smart casual"
        query = f"{gender_term} {style_term} outfit"
    
    url = "https://api.unsplash.com/photos/random"
    headers = {"Authorization": f"Client-ID {access_key}"}
    params = {"query": query, "orientation": "portrait", "count": count}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return [img["urls"]["small"] for img in response.json()]
    except Exception:
        pass
    return []

# ==========================================
# 9. SESSION STATE
# ==========================================
if "messages" not in st.session_state: st.session_state.messages = []
if "prediction" not in st.session_state: st.session_state.prediction = None
if "ai_style_query" not in st.session_state: st.session_state.ai_style_query = None

# ==========================================
# 10. USER INPUT
# ==========================================
st.markdown("## 📐 Find Your Perfect Fit")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📏 Vertical Measurements")
    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=220.0, value=170.0, step=1.0)
    leg_cm = st.number_input("Upper Leg Length (cm)", min_value=25.0, max_value=60.0, value=40.0, step=0.5)

with col2:
    st.markdown("### ⚖️ Body Measurements")
    waist_cm = st.number_input("Waist Circumference (cm)", min_value=40.0, max_value=150.0, value=75.0, step=1.0)
    arm_cm = st.number_input("Arm Length (cm)", min_value=20.0, max_value=60.0, value=36.0, step=0.5)

with col3:
    st.markdown("### ⚖️ Personal Information")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    weight_lbs = st.number_input("Weight (lbs)", min_value=60.0, max_value=350.0, value=140.0, step=1.0)
    age = st.number_input("Age", min_value=18, max_value=100, value=28, step=1)

height_inches = height_cm / 2.54

# ==========================================
# 11. PREDICTION LOGIC
# ==========================================
if st.button("✨ Find My Perfect Fit", use_container_width=True):
    with st.spinner("Analyzing your measurements..."):
        bodytype_input = pd.DataFrame([{
            "Waist_Circumference_cm": waist_cm, "Height_cm": height_cm,
            "Arm_Length_cm": arm_cm, "UpperLeg_Length_cm": leg_cm
        }])
        cluster_id = bodytype_pipeline.predict(bodytype_input)[0]
        predicted_body_type = bodytype_labels[cluster_id]

        bmi = (weight_lbs / (height_inches ** 2)) * 703
        final_body_type = predicted_body_type

        if predicted_body_type == "Tall-Heavy":
            if bmi < 18.5: final_body_type = "Slim-Tall"
            elif bmi >= 25: final_body_type = "Tall-Broad"

        size_input = pd.DataFrame([{
            "age": age, "height_inches": height_inches,
            "weight_lbs": weight_lbs, "mapped_body_type": final_body_type
        }])
        size_input = pd.get_dummies(size_input, columns=["mapped_body_type"])
        size_input = size_input.reindex(columns=size_columns, fill_value=0)
        predicted_size = size_model.predict(size_input)[0]

        st.session_state.prediction = {
            "body_type": final_body_type, "size": str(predicted_size), "gender": gender,
            "height": height_cm, "weight": weight_lbs, "waist": waist_cm,
            "arm": arm_cm, "leg": leg_cm, "age": age, "bmi": round(bmi, 2)
        }
        st.session_state.messages = []
        st.session_state.ai_style_query = None

# ==========================================
# 12. TABS AND RESULTS
# ==========================================
if st.session_state.prediction is not None:
    result = st.session_state.prediction
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📐 Fit & Size", "📸 Style Inspiration", "💬 AI Stylist"])

    # TAB 1
    with tab1:
        st.markdown("## 🎉 Your Personalized Results")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"""
            <div class="result-card">
                <p class="result-label">Your Body Shape</p>
                <p class="result-text">{result['body_type']}</p>
                <p style="color:{accent};font-weight:bold;">AI Body Type Prediction</p>
            </div>
            """, unsafe_allow_html=True)
        with res_col2:
            st.markdown(f"""
            <div class="result-card">
                <p class="result-label">Recommended Clothing Size</p>
                <p class="result-text">{result['size']}</p>
                <p style="color:{accent};font-weight:bold;">ML Size Prediction</p>
            </div>
            """, unsafe_allow_html=True)
        st.info(f"Your predicted body type is **{result['body_type']}** and your recommended size is **{result['size']}**. Always check individual brand size charts.")

    # TAB 2
    with tab2:
        st.markdown("## 📸 Outfit Inspiration")
        ai_query = st.session_state.ai_style_query
        if ai_query: st.caption(f"Showing results for your chat request: **{ai_query}**")
        else: st.caption(f"Curated styles for **{result['gender']} {result['body_type']}** shapes.")
        
        with st.spinner("Loading fashion inspiration..."):
            images = get_unsplash_images(result['body_type'], result['gender'], search_query=ai_query, count=10)
            
        if images:
            cols = st.columns(2)
            for idx, img_url in enumerate(images):
                with cols[idx % 2]:
                    st.image(img_url, use_container_width=True)
                    st.write("") 
        else:
            st.warning("Could not load images. Check Unsplash API key.")

    # TAB 3
    with tab3:
        st.markdown("## 👗 FitFinder AI Stylist")
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🔮"):
                st.markdown(message["content"])

        prompt = st.chat_input("Ask your AI Stylist anything...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🔮"):
                with st.spinner("Stylist is thinking..."):
                    try:
                        client = get_groq_client()
                        if client is None:
                            st.error("Groq API key not found.")
                        else:
                            system_prompt = f"""
                            You are FitFinder AI Stylist.
                            Gender: {result['gender']}, Body Type: {result['body_type']}, Size: {result['size']}
                            
                            Recommend outfits, colors, and styles based on these measurements.
                            CRITICAL INSTRUCTION: If the user asks about a specific clothing item or style (e.g., 'bootcut pants', 'boho'), you MUST include the exact tag [STYLE: keyword] at the VERY END of your response.
                            """
                            chat_history = [{"role": "system", "content": system_prompt}] + st.session_state.messages[-12:]
                            response = client.chat.completions.create(model="openai/gpt-oss-20b", messages=chat_history)
                            answer = response.choices[0].message.content
                            
                            import re
                            match = re.search(r'\[STYLE:\s*([^\]]+)\]', answer, re.IGNORECASE)
                            if match:
                                st.session_state.ai_style_query = match.group(1).strip()
                                answer = re.sub(r'\[STYLE:\s*[^\]]+\]', '', answer, flags=re.IGNORECASE).strip()
                            
                            st.markdown(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                            st.rerun() 
                    except Exception as e:
                        st.error(f"Groq API Error: {e}")
else:
    st.info("👆 Please enter your measurements above and click 'Find My Perfect Fit' to unlock your tabs.")