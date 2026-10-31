import streamlit as st
import pandas as pd
import joblib
from groq import Groq


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="FitFinder | AI Fashion Stylist",
    page_icon="🛍️",
    layout="wide"
)


# ==========================================
# 2. COLOR THEME - RED & BEIGE
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F5EBDD;
    color: #000000;
}

/* Chatbot messages - BLACK TEXT */
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] div {
    color: #000000 !important;
}

/* Chat input */
div[data-testid="stChatInput"] textarea {
    color: #000000 !important;
    background-color: #FFF9F0 !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #777777 !important;
}

/* Chat message background */
div[data-testid="stChatMessage"] {
    background-color: #FFF9F0;
    border: 1px solid #E6D3BD;
    border-radius: 15px;
    padding: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. HEADER
# ==========================================

st.markdown(
    '<div class="main-title">FitFinder 🛍️</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Discover Your Perfect Fit. Define Your Style.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# 4. LOAD ML MODELS
# ==========================================

@st.cache_resource
def load_models():

    bodytype_pipeline = joblib.load(
        "models/bodytype_pipeline.pkl"
    )

    bodytype_labels = joblib.load(
        "models/bodytype_labels.pkl"
    )

    size_model = joblib.load(
        "models/size_category_model.pkl"
    )

    size_columns = joblib.load(
        "models/model_columns.pkl"
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

except Exception as e:

    st.error(f"Model loading error: {e}")
    st.stop()


# ==========================================
# 5. GROQ CLIENT
# ==========================================

@st.cache_resource
def get_groq_client():

    api_key = st.secrets.get(
        "GROQ_API_KEY",
        os.getenv("GROQ_API_KEY")
    )

    if not api_key:
        return None

    return Groq(api_key=api_key)


# ==========================================
# 7. SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "prediction" not in st.session_state:
    st.session_state.prediction = None


# ==========================================
# 8. USER INPUT SECTION
# ==========================================

st.markdown("## 📐 Find Your Perfect Fit")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("### 📏 Vertical Measurements")

    height_cm = st.number_input(
        "Height (cm)",
        min_value=100.0,
        max_value=220.0,
        value=170.0,
        step=1.0
    )

    leg_cm = st.number_input(
        "Upper Leg Length (cm)",
        min_value=25.0,
        max_value=60.0,
        value=40.0,
        step=0.5
    )


with col2:

    st.markdown("### 🎯 Body Measurements")

    waist_cm = st.number_input(
        "Waist Circumference (cm)",
        min_value=40.0,
        max_value=150.0,
        value=75.0,
        step=1.0
    )

    arm_cm = st.number_input(
        "Arm Length (cm)",
        min_value=20.0,
        max_value=60.0,
        value=36.0,
        step=0.5
    )


with col3:

    st.markdown("### ⚖️ Personal Information")

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    weight_lbs = st.number_input(
        "Weight (lbs)",
        min_value=60.0,
        max_value=350.0,
        value=140.0,
        step=1.0
    )

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=28,
        step=1
    )


height_inches = height_cm / 2.54


# ==========================================
# 9. PREDICTION FUNCTION
# ==========================================

if st.button("✨ Find My Perfect Fit", use_container_width=True):

    with st.spinner("Analyzing your measurements..."):

        # BODY TYPE PREDICTION

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


        # BMI CALCULATION

        bmi = (
            weight_lbs / (height_inches ** 2)
        ) * 703

        final_body_type = predicted_body_type


        # YOUR EXISTING BODY TYPE OVERRIDE

        if predicted_body_type == "Tall-Heavy":

            if bmi < 18.5:

                final_body_type = "Slim-Tall"

            elif bmi >= 25:

                final_body_type = "Tall-Broad"


        # SIZE PREDICTION

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

        predicted_size = size_model.predict(
            size_input
        )[0]


        # SAVE RESULTS

        st.session_state.prediction = {

            "body_type": final_body_type,
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

        # Clear previous chat after a new prediction

        st.session_state.messages = []


# ==========================================
# 10. DISPLAY PREDICTION RESULTS
# ==========================================

if st.session_state.prediction is not None:

    result = st.session_state.prediction

    st.divider()

    st.markdown("## 🎉 Your Personalized Results")

    res_col1, res_col2 = st.columns(2)

    with res_col1:

        st.markdown(f"""
        <div class="result-card">
            <p class="result-label">Your Body Shape</p>
            <p class="result-text">{result['body_type']}</p>
            <p style="color:#A83232;font-weight:bold;">
                AI Body Type Prediction
            </p>
        </div>
        """, unsafe_allow_html=True)


    with res_col2:

        st.markdown(f"""
        <div class="result-card">
            <p class="result-label">Recommended Clothing Size</p>
            <p class="result-text">{result['size']}</p>
            <p style="color:#A83232;font-weight:bold;">
                ML Size Prediction
            </p>
        </div>
        """, unsafe_allow_html=True)


    st.info(
        f"Your predicted body type is **{result['body_type']}** "
        f"and your recommended size is **{result['size']}**. "
        "Always check individual brand size charts because sizing varies."
    )

    st.divider()


# ==========================================
# 11. AI STYLIST CHATBOT
# ==========================================

st.markdown("## 🧠 FitFinder AI Stylist")

st.caption(
    "Your personal fashion assistant. Ask anything about your "
    "predicted fit, clothing sizes, outfits and styling."
)


if st.session_state.prediction is None:

    st.info(
        "👋 First, complete your measurements and click "
        "'Find My Perfect Fit'. Then you can chat with your AI Stylist."
    )


# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar="🧑" if message["role"] == "user" else "👗"
    ):

        st.markdown(message["content"])


# CHAT INPUT - ALWAYS OUTSIDE CONDITIONAL BLOCKS

prompt = st.chat_input(
    "Ask your AI Stylist anything..."
)


if prompt:

    if st.session_state.prediction is None:

        st.warning(
            "Please generate your FitFinder prediction first!"
        )

    else:

        # ADD USER MESSAGE

        st.session_state.messages.append({

            "role": "user",
            "content": prompt

        })

        with st.chat_message("user", avatar="🧑"):

            st.markdown(prompt)


        # GROQ RESPONSE

        with st.chat_message("assistant", avatar="👗"):

            with st.spinner("Your stylist is thinking..."):

                try:

                    client = get_groq_client()

                    if client is None:

                        st.error(
                            "Groq API key not found. "
                            "Please configure your API key."
                        )

                    else:

                        # PERSONALIZED SYSTEM PROMPT

                        system_prompt = f"""
                        You are FitFinder AI Stylist, a friendly and knowledgeable
                        fashion assistant.

                        You are helping a user with the following ML predictions
                        and measurements:

                        Gender: {result['gender']}
                        Body Type: {result['body_type']}
                        Recommended Size: {result['size']}

                        Height: {result['height']} cm
                        Weight: {result['weight']} lbs
                        Waist: {result['waist']} cm
                        Arm Length: {result['arm']} cm
                        Upper Leg Length: {result['leg']} cm
                        Age: {result['age']}


YOUR RESPONSIBILITIES:

1. Recommend outfits based on the predicted body type.
2. Explain why a clothing size may suit the user.
3. Suggest casual, formal, streetwear and seasonal outfits.
4. Recommend suitable clothing colors and combinations.
5. Answer follow-up questions using the conversation history.
6. Explain fashion and styling concepts simply.

IMPORTANT RULES:

- Be friendly, conversational and practical.
- Remember the user's previous questions.
- Use the supplied ML prediction as context, not as a
  guaranteed measurement of real-world fit.
- Do not change the predicted size unless explaining
  that a brand's size chart may differ.
- Never make medical judgments based on body measurements.
- If a question is unrelated to fashion, politely guide
  the conversation back to fashion.
- Consider the user's selected gender when giving fashion recommendations.
- Give recommendations based on gender, body type, size, and measurements.
- Do not assume the user's preferences only from gender; adapt when they specify a style preference.

Keep answers clear and well organized.
Use bullet points when useful.
"""


                        # SEND CONVERSATION HISTORY

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

                        answer = response.choices[0].message.content

                        st.markdown(answer)


                        # SAVE ASSISTANT RESPONSE

                        st.session_state.messages.append({

                            "role": "assistant",
                            "content": answer

                        })


                except Exception as e:

                    st.error(f"Groq API Error: {e}")


# ==========================================
# 12. SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 🛍️ FitFinder")

    st.caption("AI-Powered Fashion Assistant")

    st.divider()

    st.markdown("### About")

    st.write(
        "FitFinder uses Machine Learning to predict body "
        "types and recommend clothing sizes."
    )

    st.divider()

    st.markdown("### AI Stylist")

    st.write(
        "Chat with your personal AI stylist for outfit "
        "recommendations and fashion advice."
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.caption("FitFinder © 2026")