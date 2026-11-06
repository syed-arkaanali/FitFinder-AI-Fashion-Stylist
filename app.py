import streamlit as st
import os
import re

# Import our custom modules
from style import apply_theme
from ml_engine import load_models, predict_fit
from ai_engine import get_groq_client, get_unsplash_images

# ==========================================
# 1. PAGE CONFIG & THEME
# ==========================================
st.set_page_config(page_title="FitFinder | AI Fashion Stylist", page_icon="👕", layout="wide")
apply_theme()

# ==========================================
# 2. SIDEBAR
# ==========================================
with st.sidebar:
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "Indian_art.jpeg")
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
    except Exception:
        pass
        
    st.divider()
    st.markdown("## 👕 FitFinder")
    st.caption("AI-Powered Fashion Assistant")
    st.divider()
    st.markdown("### About")
    st.write("FitFinder uses Machine Learning to predict body types and recommend clothing sizes.")
    st.divider()
    
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("FitFinder © 2026")

# ==========================================
# 3. LOAD MODELS
# ==========================================
try:
    bodytype_pipeline, bodytype_labels, size_model, size_columns = load_models()
except Exception as e:
    st.error(f"Model loading error: {e}")
    st.stop()

# ==========================================
# 4. SESSION STATE
# ==========================================
if "messages" not in st.session_state: st.session_state.messages = []
if "prediction" not in st.session_state: st.session_state.prediction = None
if "ai_style_query" not in st.session_state: st.session_state.ai_style_query = None

# ==========================================
# 5. HEADER & INPUTS
# ==========================================
st.markdown('<h1 style="text-align: center;">FitFinder 👕</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 18px;">Discover Your Perfect Fit. Define Your Style.</p>', unsafe_allow_html=True)

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
# 6. PREDICTION LOGIC
# ==========================================
if st.button("✨ Find My Perfect Fit", use_container_width=True):
    with st.spinner("Analyzing your measurements..."):
        
        # Call the modular ML engine
        results = predict_fit(
            bodytype_pipeline, bodytype_labels, size_model, size_columns, 
            waist_cm, height_cm, arm_cm, leg_cm, age, weight_lbs, height_inches
        )
        
        # Save to session state
        st.session_state.prediction = {
            "body_type": results["body_type"], 
            "size": results["size"], 
            "gender": gender,
            "height": height_cm, 
            "weight": weight_lbs, 
            "waist": waist_cm,
            "arm": arm_cm, 
            "leg": leg_cm, 
            "age": age, 
            "bmi": results["bmi"]
        }
        st.session_state.messages = []
        st.session_state.ai_style_query = None

# ==========================================
# 7. TABS & DISPLAY
# ==========================================
if st.session_state.prediction is not None:
    result = st.session_state.prediction
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📐 Fit & Size", "📸 Style Inspiration", "💬 AI Stylist"])

    # TAB 1: FIT & SIZE
    with tab1:
        st.markdown("## 🎉 Your Personalized Results")
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.markdown(f"""
            <div class="result-card">
                <p class="result-label">Your Body Shape</p>
                <p class="result-text">{result['body_type']}</p>
                <p style="color:#C12B2B;font-weight:bold;">AI Body Type Prediction</p>
            </div>
            """, unsafe_allow_html=True)
            
        with res_col2:
            st.markdown(f"""
            <div class="result-card">
                <p class="result-label">Recommended Clothing Size</p>
                <p class="result-text">{result['size']}</p>
                <p style="color:#C12B2B;font-weight:bold;">ML Size Prediction</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Using st.html to bypass Streamlit's CSS constraints
        st.html(f"""
        <div style="background-color: #691313; padding: 15px; border-radius: 10px; border-left: 5px solid #C12B2B; margin-top: 20px;">
            <p style="color: #FFDC9C !important; margin: 0; font-size: 16px; font-family: sans-serif;">
                Your predicted body type is <b>{result['body_type']}</b> and your recommended size is <b>{result['size']}</b>. Always check individual brand size charts.
            </p>
        </div>
        """)
        
    # TAB 2: STYLE INSPIRATION
    with tab2:
        st.markdown("## 📸 Outfit Inspiration")
        ai_query = st.session_state.ai_style_query
        
        if ai_query: 
            st.caption(f"Showing results for your chat request: **{ai_query}**")
        else: 
            st.caption(f"Curated styles for **{result['gender']} {result['body_type']}** shapes.")
        
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

    # TAB 3: AI STYLIST
    with tab3:
        st.markdown("## 👗 FitFinder AI Stylist")
        st.caption("Your personal fashion assistant.")
        
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