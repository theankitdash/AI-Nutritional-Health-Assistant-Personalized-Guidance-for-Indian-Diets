import httpx
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq API configuration
INVOKE_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")


async def call_groq_api(
    messages: list,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    model: str = None,
) -> str:
    """Async Groq API call using httpx (non-blocking)."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in the environment or .env file.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model or MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(INVOKE_URL, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()

            if "choices" not in result:
                if "error" in result:
                    error_msg = result["error"]
                    if isinstance(error_msg, dict):
                        raise Exception(f"Groq API Error: {error_msg.get('message', str(error_msg))}")
                    else:
                        raise Exception(f"Groq API Error: {error_msg}")
                else:
                    raise Exception(f"Unexpected API response format: {result}")

            return result["choices"][0]["message"]["content"]

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        raise Exception(f"Groq API HTTP Error: {e}")
    except httpx.RequestError as e:
        print(f"Request Error: {e}")
        raise Exception(f"Groq API Request Error: {e}")
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        raise
