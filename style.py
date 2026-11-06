import streamlit as st

def apply_theme():
    # MAIN COLORS (Light Peach background, Dark Maroon text)
    bg_color = "#FFDC9C"       # Light peach background
    text_color = "#691313"     # Dark maroon text
    
    # SIDEBAR COLORS (Dark Maroon background, Light Peach text)
    sidebar_bg = "#691313"     # Dark maroon sidebar
    sidebar_text = "#FFDC9C"   # Light peach text inside sidebar
    
    # BUTTON COLORS
    main_btn_bg = "#691313"    # Dark maroon button
    main_btn_text = "#FFDC9C"  # Light peach text on button
    
    sidebar_btn_bg = "#FFDC9C" # Light peach sidebar button
    sidebar_btn_text = "#691313" # Dark maroon text on sidebar button
    
    # CARD COLORS
    card_bg = "#FFF9F0"        # Very light cream/peach for cards
    accent = "#C12B2B"         # Strong red for borders

    st.markdown(f"""
    <style>
    /* Main App Background & Text */
    .stApp {{ 
        background-color: {bg_color}; 
        color: {text_color}; 
    }}
    
    /* Force ALL main text to be Dark Maroon */
    h1, h2, h3, p, span, div, label {{ 
        color: {text_color} !important; 
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{ 
        background-color: {sidebar_bg} !important; 
    }}
    
    /* Force ALL Sidebar text to be Light Peach */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {{ 
        color: {sidebar_text} !important; 
    }}
    
    /* Clear Chat Button in Sidebar */
    [data-testid="stSidebar"] .stButton > button {{
        background-color: {sidebar_btn_bg} !important;
        border: none;
    }}
    [data-testid="stSidebar"] .stButton > button p, 
    [data-testid="stSidebar"] .stButton > button div, 
    [data-testid="stSidebar"] .stButton > button span {{
        color: {sidebar_btn_text} !important;
        font-weight: bold;
    }}
    
    /* Chat Message Styling */
    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span, 
    div[data-testid="stChatMessage"] div {{ 
        color: {text_color} !important; 
    }}
    
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
        color: {text_color} !important;
    }}
    
    /* Main "Find My Perfect Fit" Button */
    .stButton > button {{
        background-color: {main_btn_bg} !important; 
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }}
    
    .stButton > button p, 
    .stButton > button div, 
    .stButton > button span {{
        color: {main_btn_text} !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }}
    
    .stButton > button:hover {{
        opacity: 0.8;
    }}
    </style>
    """, unsafe_allow_html=True)