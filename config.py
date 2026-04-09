import os
import streamlit as st
from dotenv import load_dotenv

# ---- LOAD ENV (LOCAL ONLY) ----
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# ---- GROQ API KEY HANDLING ----
def get_groq_key():
    # 1️⃣ Try .env FIRST (for local)
    groq_key = os.getenv("GROQ_API_KEY")

    # 2️⃣ Then try Streamlit secrets (for cloud)
    if not groq_key:
        try:
            groq_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            groq_key = None

    return groq_key

GROQ_API_KEY = get_groq_key()

# ---- SAFETY CHECK ----
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing. Add it in .env (local) or Streamlit Secrets (cloud).")
    st.stop()

# ---- CONFIG SETTINGS ----
CONFIDENCE_THRESHOLD = 0.80
MAX_DEPTH_FAST = 2
MAX_DEPTH_DEEP = 4
FAST_PAPERS_PER_QUERY = 8
DEEP_PAPERS_PER_QUERY = 15

MODEL_NAME = "llama-3.3-70b-versatile"
OPENALEX_EMAIL = "scholarpulse@research.ai"

# ---- FAST MODE OPTIMIZATION ----
FAST_MODE_TIMEOUT = 85
FAST_CRITIQUE_BATCH_SIZE = 3
MAX_CONTRADICTION_PAIRS_FAST = 5

MODEL_NAME_FAST = "llama-3.1-8b-instant"
MODEL_NAME_REASONING = "llama-3.3-70b-versatile"