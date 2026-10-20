from dotenv import load_dotenv

load_dotenv()

from agent.clients.llm import ask_json

out = ask_json(
    "You are a code reviewer.",
    'Review this line and return {"severity": "low|medium|high", "comment": str}: '
    "password = 'admin123'",
)
print(out)