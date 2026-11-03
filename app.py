
import os
import re
from pathlib import Path

import streamlit as st
import pandas as pd
import joblib
import requests
from groq import Groq


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="FitFinder | AI Fashion Stylist",
    page_icon="👕",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 2. COLOR THEME
# ==========================================

BEIGE = "#F2E3C6"
MAROON = "#641E35"
DARK_MAROON = "#451326"
LIGHT_BEIGE = "#FAF2E5"

# ==========================================
# 3. CUSTOM CSS
# ==========================================

st.markdown(f"""
<style>

.stApp {{
    background-color: {BEIGE};
    color: {MAROON};
}}

.stApp p,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp label,
.stApp li,
.stApp .stMarkdown {{
    color: {MAROON};
}}

[data-testid="stSidebar"] {{
    background-color: {MAROON};
}}

[data-testid="stSidebar"] * {{
    color: {BEIGE} !important;
}}

.stButton > button {{
    background-color: {MAROON};
    color: {BEIGE} !important;
    border: 1px solid {MAROON};
    border-radius: 10px;
    font-weight: bold;
    padding: 10px 20px;
}}

.stButton > button:hover {{
    background-color: {DARK_MAROON};
    color: {BEIGE} !important;
    border: 1px solid {BEIGE};
}}

.stTextInput input,
.stNumberInput input,
.stChatInput textarea {{
    background-color: {LIGHT_BEIGE} !important;
    color: {MAROON} !important;
    border: 1px solid {MAROON};
}}

.stSelectbox div[data-baseweb="select"] {{
    background-color: {LIGHT_BEIGE};
    color: {MAROON};
}}

.result-card {{
    background-color: {MAROON};
    color: {BEIGE};
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 15px;
    min-height: 155px;
}}

.result-card p,
.result-card h2,
.result-card h1 {{
    color: {BEIGE} !important;
}}

.result-label {{
    font-size: 14px;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

.result-text {{
    font-size: 32px;
    font-weight: bold;
}}

.info-card {{
    background-color: {LIGHT_BEIGE};
    color: {MAROON};
    border: 1px solid {MAROON};
    padding: 18px;
    border-radius: 12px;
}}

.info-card h3,
.info-card p {{
    color: {MAROON} !important;
}}

div[data-testid="stChatMessage"] {{
    background-color: {LIGHT_BEIGE};
    border: 1px solid {MAROON};
    border-radius: 12px;
    padding: 12px;
}}

div[data-testid="stChatMessage"] * {{
    color: {MAROON} !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    background-color: {BEIGE};
}}

.stTabs [data-baseweb="tab"] {{
    color: {BEIGE} !important;
}}

.stTabs [aria-selected="true"] {{
    background-color: {BEIGE};
    color: {BEIGE} !important;
}}

div[data-testid="stMetric"] {{
    background-color: {MAROON};
    padding: 15px;
    border-radius: 12px;
}}

div[data-testid="stMetric"] * {{
    color: {BEIGE} !important;
}}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "ai_style_query" not in st.session_state:
    st.session_state.ai_style_query = None


# ==========================================
# 5. API CONFIGURATION
# ==========================================

def get_secret(name):
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None

    return value or os.getenv(name)


def get_groq_client():
    api_key = get_secret("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


# ==========================================
# 6. LOAD ML MODELS
# ==========================================

@st.cache_resource
def load_models():

    bodytype_pipeline = joblib.load(
        BASE_DIR / "models" / "bodytype_pipeline.pkl"
    )

    bodytype_labels = joblib.load(
        BASE_DIR / "models" / "bodytype_labels.pkl"
    )

    size_model = joblib.load(
        BASE_DIR / "models" / "size_category_model.pkl"
    )

    size_columns = joblib.load(
        BASE_DIR / "models" / "model_columns.pkl"
    )

    return (
        bodytype_pipeline,
        bodytype_labels,
        size_model,
        size_columns
    )


try:
    (
        bodytype_pipeline,
        bodytype_labels,
        size_model,
        size_columns
    ) = load_models()

except Exception as error:
    st.error(f"Model loading error: {error}")
    st.stop()


# ==========================================
# 7. UNSPLASH IMAGE FUNCTION
# ==========================================

@st.cache_data(show_spinner=False)
def get_unsplash_images(
    access_key,
    body_type,
    gender,
    search_query=None,
    count=10
):

    if not access_key:
        return []

    gender_term = (
        "men" if gender == "Male"
        else "women" if gender == "Female"
        else "fashion"
    )

    if search_query:
        query = f"{gender_term} {search_query}"

    else:
        body_term = body_type.lower()

        if "broad" in body_term or "heavy" in body_term:
            style = "oversized tailored streetwear"

        elif "petite" in body_term:
            style = "high waisted outfits"

        elif "slim" in body_term:
            style = "layered minimalist fashion"

        else:
            style = "classic smart casual outfits"

        query = f"{gender_term} {style}"

    try:

        response = requests.get(
            "https://api.unsplash.com/search/photos",
            headers={
                "Authorization": f"Client-ID {access_key}"
            },
            params={
                "query": query,
                "per_page": count,
                "orientation": "portrait"
            },
            timeout=15
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        return [
            item["urls"]["regular"]
            for item in results
            if item.get("urls", {}).get("regular")
        ]

    except requests.RequestException:
        return []


# ==========================================
# 8. SIDEBAR
# ==========================================

with st.sidebar:

    image_path = BASE_DIR / "Indian_art.jpeg"

    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.warning("Image not found.")

    st.divider()

    st.title("👕 FitFinder")

    st.caption("AI-Powered Fashion Assistant")

    st.divider()

    st.markdown("### About")

    st.write(
        "FitFinder uses Machine Learning to predict "
        "body types and recommend clothing sizes."
    )

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.ai_style_query = None
        st.rerun()

    st.caption("FitFinder © 2026")


# ==========================================
# 9. HEADER
# ==========================================

st.markdown(
    f"""
    <h1 style="text-align:center; color:{MAROON};">
        FitFinder 👕
    </h1>
    <p style="text-align:center; color:{MAROON};
    font-size:18px;">
        Discover Your Perfect Fit. Define Your Style.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 10. USER MEASUREMENTS
# ==========================================

st.markdown("## 📐 Find Your Perfect Fit")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("### 📏 Vertical Measurements")

    height_cm = st.number_input(
        "Height (cm)",
        100.0, 220.0, 170.0, step=1.0
    )

    leg_cm = st.number_input(
        "Upper Leg Length (cm)",
        25.0, 60.0, 40.0, step=0.5
    )

with col2:

    st.markdown("### ⚖️ Body Measurements")

    waist_cm = st.number_input(
        "Waist Circumference (cm)",
        40.0, 150.0, 75.0, step=1.0
    )

    arm_cm = st.number_input(
        "Arm Length (cm)",
        20.0, 60.0, 36.0, step=0.5
    )

with col3:

    st.markdown("### 👤 Personal Information")

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    weight_lbs = st.number_input(
        "Weight (lbs)",
        60.0, 350.0, 140.0, step=1.0
    )

    age = st.number_input(
        "Age",
        18, 100, 28
    )


# ==========================================
# 11. ML PREDICTION
# ==========================================

if st.button("✨ Find My Perfect Fit", use_container_width=True):

    with st.spinner("Analyzing your measurements..."):

        try:

            height_inches = height_cm / 2.54

            bodytype_input = pd.DataFrame([{
                "Waist_Circumference_cm": waist_cm,
                "Height_cm": height_cm,
                "Arm_Length_cm": arm_cm,
                "UpperLeg_Length_cm": leg_cm
            }])

            cluster_id = bodytype_pipeline.predict(
                bodytype_input
            )[0]

            predicted_body_type = bodytype_labels[cluster_id]

            bmi = (
                weight_lbs / (height_inches ** 2)
            ) * 703

            final_body_type = predicted_body_type

            # Existing FitFinder body-type adjustment
            if predicted_body_type == "Tall-Heavy" and bmi < 18.5:
                final_body_type = "Slim-Tall"

            # Size prediction
            size_input = pd.DataFrame([{
                "age": age,
                "height_inches": height_inches,
                "weight_lbs": weight_lbs,
                "mapped_body_type": final_body_type
            }])

            size_input = pd.get_dummies(
                size_input,
                columns=["mapped_body_type"]
            )

            size_input = size_input.reindex(
                columns=size_columns,
                fill_value=0
            )

            predicted_size = size_model.predict(size_input)[0]

            # Save prediction
            st.session_state.prediction = {
                "body_type": str(final_body_type),
                "size": str(predicted_size),
                "gender": gender,
                "height": height_cm,
                "weight": weight_lbs,
                "waist": waist_cm,
                "arm": arm_cm,
                "leg": leg_cm,
                "age": age,
                "bmi": round(bmi, 2)
            }

            st.session_state.messages = []
            st.session_state.ai_style_query = None

        except Exception as error:

            st.error(f"Prediction error: {error}")



# ==========================================
# 12. TABS AND RESULTS
# ==========================================

tab1, tab2, tab3 = st.tabs([
    "📐 Fit & Size",
    "📸 Style Inspiration",
    "💬 AI Stylist"
])


# ------------------------------------------
# TAB 1: PERSONALIZED FIT & SIZE
# ------------------------------------------

with tab1:

    if st.session_state.prediction is not None:

        result = st.session_state.prediction

        st.markdown("## 🎉 Your Personalized Results")

        res_col1, res_col2 = st.columns(2)

        with res_col1:

            st.markdown(
                f"""
                <div class="result-card">
                    <p class="result-label">Your Body Shape</p>
                    <h1 class="result-text">
                        {result['body_type']}
                    </h1>
                    <p>AI Body Type Prediction</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with res_col2:

            st.markdown(
                f"""
                <div class="result-card">
                    <p class="result-label">
                        Recommended Clothing Size
                    </p>
                    <h1 class="result-text">
                        {result['size']}
                    </h1>
                    <p>ML Size Prediction</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("### 📊 Your Body Profile")

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric("BMI", result["bmi"])

        with metric2:
            st.metric("Height", f"{result['height']} cm")

        with metric3:
            st.metric("Weight", f"{result['weight']} lbs")

        st.divider()

        st.markdown("### 📏 Your Measurement Details")

        detail1, detail2, detail3 = st.columns(3)

        with detail1:
            st.metric("Waist", f"{result['waist']} cm")

        with detail2:
            st.metric("Arm Length", f"{result['arm']} cm")

        with detail3:
            st.metric("Upper Leg", f"{result['leg']} cm")

        st.divider()

        st.markdown("### 👗 Your Fit Recommendation")

        st.success(
            f"Your ML model recommends **{result['size']}** "
            f"for your predicted **{result['body_type']}** body type."
        )

        st.info(
            "This is an ML-based size estimate. Actual clothing "
            "sizes vary between brands and garment styles. "
            "Always check the brand's size chart."
        )

    else:

        st.info(
            "👆 Enter your measurements above and click "
            "'Find My Perfect Fit' to see your personalized results."
        )


# ------------------------------------------
# TAB 2: STYLE INSPIRATION
# ------------------------------------------

with tab2:

    st.markdown("## 📸 Outfit Inspiration")

    if st.session_state.prediction is not None:

        result = st.session_state.prediction

        ai_query = st.session_state.ai_style_query

        if ai_query:

            st.caption(
                f"Showing fashion inspiration for: **{ai_query}**"
            )

        else:

            st.caption(
                f"Curated styles for **{result['gender']} "
                f"{result['body_type']}** body shape."
            )

        access_key = get_secret("UNSPLASH_ACCESS_KEY")

        with st.spinner("Loading fashion inspiration..."):

            images = get_unsplash_images(
                access_key,
                result["body_type"],
                result["gender"],
                search_query=ai_query,
                count=10
            )

        if images:

            cols = st.columns(2)

            for index, image_url in enumerate(images):

                with cols[index % 2]:

                    st.image(
                        image_url,
                        use_container_width=True
                    )

        else:

            st.warning(
                "Could not load images. Please check your "
                "Unsplash API key and API request limits."
            )

    else:

        st.info(
            "Complete your measurements first to unlock "
            "personalized fashion inspiration."
        )


# ------------------------------------------
# TAB 3: AI STYLIST
# ------------------------------------------

with tab3:

    st.markdown("## 👗 FitFinder AI Stylist")

    if st.session_state.prediction is not None:

        result = st.session_state.prediction

        # Display previous messages

        for message in st.session_state.messages:

            avatar = (
                "👤" if message["role"] == "user"
                else "🔮"
            )

            with st.chat_message(
                message["role"],
                avatar=avatar
            ):

                st.markdown(message["content"])

        # Chat input

        prompt = st.chat_input(
            "Ask your AI Stylist anything..."
        )

        if prompt:

            st.session_state.ai_style_query = None

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🔮"):

                with st.spinner("Your stylist is thinking..."):

                    try:

                        client = get_groq_client()

                        if client is None:

                            st.error(
                                "Groq API key not found. "
                                "Configure GROQ_API_KEY in Streamlit Secrets."
                            )

                        else:

                            system_prompt = f"""
You are FitFinder AI Stylist.

User Profile:
Gender: {result['gender']}
Body Type: {result['body_type']}
Recommended Size: {result['size']}

Give friendly and practical fashion recommendations.

Suggest suitable outfits, colors, fabrics and styling ideas.

Use the user's body type and size when relevant.

If the user asks about a specific clothing item or
fashion style, add a final tag in exactly this format:

[STYLE: keyword]

The tag must be the very last part of your response.

Do not add this tag for unrelated questions.
"""

                            chat_history = [
                                {
                                    "role": "system",
                                    "content": system_prompt
                                }
                            ] + st.session_state.messages[-12:]

                            response = client.chat.completions.create(
                                model="openai/gpt-oss-20b",
                                messages=chat_history
                            )

                            answer = (
                                response.choices[0].message.content or ""
                            ).strip()

                            # Extract style keyword

                            match = re.search(
                                r"\[STYLE:\s*(.*?)\]",
                                answer,
                                flags=re.IGNORECASE
                            )

                            if match:

                                keyword = match.group(1).strip()

                                if keyword:
                                    st.session_state.ai_style_query = keyword

                                answer = re.sub(
                                    r"\[STYLE:\s*.*?\]",
                                    "",
                                    answer,
                                    flags=re.IGNORECASE
                                ).strip()

                            if not answer:
                                answer = "Please try asking another question."

                            st.markdown(answer)

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer
                            })

                            st.rerun()

                    except Exception as error:

                        st.error(f"Groq API Error: {error}")

    else:

        st.info(
            "Complete your measurements first to unlock "
            "your personalized AI Stylist."
        )


# ==========================================
# 13. FOOTER
# ==========================================

st.divider()

st.caption(
    "FitFinder © 2026 | Your Personal AI Fashion Assistant"
)