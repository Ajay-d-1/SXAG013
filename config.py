import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Keep for backwards compatibility
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
CONFIDENCE_THRESHOLD = 0.80
MAX_DEPTH_FAST = 2
MAX_DEPTH_DEEP = 4
FAST_PAPERS_PER_QUERY = 8
DEEP_PAPERS_PER_QUERY = 15
MODEL_NAME = "llama-3.3-70b-versatile"
OPENALEX_EMAIL = "scholarpulse@research.ai"
