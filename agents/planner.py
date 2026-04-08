from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME
from utils.prompts import PLANNER_PROMPT
from demo_data import get_demo_topic, get_demo_data
import json


class PlannerAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def plan(self, topic: str) -> dict:
        # Check for demo topic first
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
            text = text.removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Planner error: {e}")
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
                "rationale": "Default decomposition"
            }


if __name__ == "__main__":
    agent = PlannerAgent()
    result = agent.plan("AI in Rural Healthcare")
    print(json.dumps(result, indent=2))
