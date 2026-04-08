import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
client = Groq(api_key=key)

models = client.models.list()
for m in models.data:
    print(m.id)
