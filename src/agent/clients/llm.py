import json
import os
import time

from groq import Groq

# Model names change often: check console.groq.com and set GROQ_MODEL in .env
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def ask_json(system: str, user: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    t0 = time.perf_counter()
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system + " Respond only with valid JSON."},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return {
        "data": json.loads(r.choices[0].message.content),
        "latency_s": round(time.perf_counter() - t0, 2),
        "tokens": r.usage.total_tokens,
        "prompt_tokens": r.usage.prompt_tokens,
        "completion_tokens": r.usage.completion_tokens,
    }