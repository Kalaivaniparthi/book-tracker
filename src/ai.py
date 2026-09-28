import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

MODEL = "qwen/qwen3.8-27b"


def summarize(description: str) -> str:
    """Return a one-sentence summary of a book description."""
    if not description or description.strip() == "":
        return "No description available."

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "/no_think "
                        "You are a book summarizer. "
                        "Reply with ONE short sentence (max 20 words). "
                        "No quotes, no preamble, just the sentence."
                    ),
                },
                {"role": "user", "content": description[:1500]},
            ],
            temperature=0.5,
            max_tokens=200,
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            return "Summary unavailable."
        return content.strip()
    except Exception as e:
        print(f"  AI error: {e}")
        return "Summary unavailable."
