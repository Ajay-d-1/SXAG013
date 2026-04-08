import os
import streamlit as st
from dotenv import load_dotenv

# Load .env for local development
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# ---- GROQ API KEY HANDLING ----
def get_groq_key():
    try:
        # For Streamlit Cloud
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        # For local (.env)
        return os.getenv("GROQ_API_KEY")

GROQ_API_KEY = get_groq_key()

# ---- CONFIG SETTINGS ----
CONFIDENCE_THRESHOLD = 0.80
MAX_DEPTH_FAST = 2
MAX_DEPTH_DEEP = 4
FAST_PAPERS_PER_QUERY = 8
DEEP_PAPERS_PER_QUERY = 15
MODEL_NAME = "llama-3.3-70b-versatile"
OPENALEX_EMAIL = "scholarpulse@research.ai"