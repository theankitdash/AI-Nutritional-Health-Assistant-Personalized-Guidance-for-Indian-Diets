import requests
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# NVIDIA API configuration
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "google/gemma-4-31b-it"


def _call_nvidia_api_sync(
    messages: list,
    max_tokens: int = 16384,
    temperature: float = 1.0,
) -> str:
    """Synchronous NVIDIA API call (runs in a thread to avoid blocking)."""
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.95,
        "stream": False,
    }

    response = requests.post(INVOKE_URL, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()

    if "choices" not in result:
        if "error" in result:
            error_msg = result["error"]
            if isinstance(error_msg, dict):
                raise Exception(f"NVIDIA API Error: {error_msg.get('message', str(error_msg))}")
            else:
                raise Exception(f"NVIDIA API Error: {error_msg}")
        else:
            raise Exception(f"Unexpected API response format: {result}")

    return result["choices"][0]["message"]["content"]


async def call_nvidia_api(
    messages: list,
    max_tokens: int = 16384,
    temperature: float = 1.0,
) -> str:
    """Async wrapper — runs the requests call in a thread so it doesn't block the event loop."""
    try:
        return await asyncio.to_thread(
            _call_nvidia_api_sync, messages, max_tokens, temperature
        )
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        raise Exception(f"NVIDIA API HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        raise Exception(f"NVIDIA API Request Error: {e}")
    except Exception as e:
        print(f"Error calling NVIDIA API: {e}")
        raise
