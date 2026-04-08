from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME
from utils.prompts import PLANNER_PROMPT
from demo_data import get_demo_topic, get_demo_data
import json


class PlannerAgent:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("❌ GROQ_API_KEY is missing. Check your .env or Streamlit secrets.")
        
        self.client = Groq(api_key=GROQ_API_KEY)

    def plan(self, topic: str) -> dict:
        # ---- DEMO MODE CHECK ----
        demo_key = get_demo_topic(topic)
        if demo_key:
            print(f"[DEMO MODE] Using pre-loaded plan for: {demo_key}")
            data = get_demo_data(demo_key)
            if data:
                return {
                    "sub_questions": data.get("sub_questions", []),
                    "search_queries": [demo_key],
                    "rationale": "Demo mode: using pre-loaded research questions"
                }

        # ---- REAL API CALL ----
        try:
            completion = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": PLANNER_PROMPT},
                    {"role": "user", "content": topic}
                ],
                response_format={"type": "json_object"}
            )

            text = completion.choices[0].message.content.strip()

            # Clean markdown formatting if present
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            return json.loads(text)

        except Exception as e:
            print(f"⚠️ Planner error: {e}")

            # ---- FALLBACK SAFE RESPONSE ----
            return {
                "sub_questions": [
                    f"What methods are used in {topic}?",
                    f"What datasets exist for {topic}?",
                    f"What are the main challenges in {topic}?",
                    f"What are the most impactful recent advances in {topic}?",
                    f"What practical applications exist for {topic}?"
                ],
                "search_queries": [
                    topic,
                    f"{topic} methods",
                    f"{topic} challenges",
                    f"{topic} recent advances 2024",
                    f"{topic} applications"
                ],
                "rationale": "Fallback due to API error"
            }


# ---- LOCAL TEST ----
if __name__ == "__main__":
    agent = PlannerAgent()
    result = agent.plan("AI in Rural Healthcare")
    print(json.dumps(result, indent=2))