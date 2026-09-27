import os
from dotenv import load_dotenv
import httpx

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Active Groq models on your account: qwen/qwen3.8-27b, openai/gpt-oss-120b, openai/gpt-oss-20b
MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

print("Testing Groq API...")
print(f"Model: {MODEL_NAME}")
print(f"API Key (first 10 chars): {GROQ_API_KEY[:10] if GROQ_API_KEY else 'None'}...")
print("\nSending request...\n")

def get_available_models():
    """Fetch all active models from Groq."""
    try:
        res = httpx.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            timeout=10.0
        )
        if res.status_code == 200:
            return sorted([m["id"] for m in res.json().get("data", [])])
    except Exception:
        pass
    return []

try:
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": "Explain why fast inference is critical for reasoning models in 2-3 sentences."
            }
        ]
    )
    print("✓ Success! Response:\n")
    print(completion.choices[0].message.content)

except Exception as e:
    print(f"\n✗ Exception: {e}")
    if "404" in str(e) or "model_not_found" in str(e):
        print(f"\n[!] Model '{MODEL_NAME}' not found or deprecated on Groq.")
        available = get_available_models()
        if available:
            print(f"\nAvailable active models on your Groq account:")
            for m in available:
                print(f"  • {m}")
            print(f"\nTip: Set GROQ_MODEL in .env or change MODEL_NAME to one of the above.")
