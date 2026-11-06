import streamlit as st

def apply_theme():
    bg_color = "#FFB989"       # Pink/Peach background
    text_color = "#691313"     # Very dark maroon for text
    card_bg = "#FFDC9C"        # Lightest peach for cards
    accent = "#C12B2B"         # Strong red for accents
    btn_bg = "#691313"         # Dark maroon for buttons
    btn_text = "#FFFFFF"       # White text on buttons
    sidebar_bg = "#FFDC9C"     # Light peach sidebar

    st.markdown(f"""
    <style>
    /* Global App Background */
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    
    /* Global Text Colors */
    h1, h2, h3, p, span, div {{ color: {text_color}; }}
    
    /* Sidebar Background */
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
    
    /* Chat Message Styling */
    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span, 
    div[data-testid="stChatMessage"] div {{ color: {text_color} !important; }}
    
    div[data-testid="stChatMessage"] {{
        background-color: {card_bg}; 
        border: 1px solid {accent}; 
        border-radius: 15px; 
        padding: 12px;
    }}
    
    /* Chat Input */
    div[data-testid="stChatInput"] textarea {{
        color: {text_color} !important; 
        background-color: {card_bg} !important;
    }}
    
    /* Result Cards */
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
    
    /* BUTTON FIX */
    .stButton > button {{
        background-color: {btn_bg} !important; 
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }}
    
    /* Force the text inside the button to be white */
    .stButton > button p, 
    .stButton > button div, 
    .stButton > button span {{
        color: {btn_text} !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }}
    
    .stButton > button:hover {{
        opacity: 0.8;
    }}
    </style>
    """, unsafe_allow_html=True)