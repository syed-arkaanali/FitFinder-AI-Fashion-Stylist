import os
import requests
import streamlit as st
from groq import Groq

@st.cache_resource
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key:
        return None
    return Groq(api_key=api_key)

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