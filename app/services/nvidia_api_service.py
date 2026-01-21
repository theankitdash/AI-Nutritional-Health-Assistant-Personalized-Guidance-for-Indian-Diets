import requests
import os
from dotenv import load_dotenv

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# NVIDIA API configuration
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "google/gemma-3-27b-it"

def call_nvidia_api(messages: list, stream: bool = False) -> str:
    """Call NVIDIA API with the given messages."""
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "text/event-stream" if stream else "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.20,
        "top_p": 0.70,
        "stream": stream
    }
    
    try:
        response = requests.post(INVOKE_URL, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        
        if stream:
            # Handle streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    full_response += line.decode("utf-8") + "\n"
            return full_response
        else:
            # Handle non-streaming response
            result = response.json()
            
            # Check if response has the expected structure
            if "choices" not in result:
                # Log the actual response for debugging
                print(f"Unexpected API response: {result}")
                
                # Check for error message in response
                if "error" in result:
                    error_msg = result["error"]
                    if isinstance(error_msg, dict):
                        raise Exception(f"NVIDIA API Error: {error_msg.get('message', str(error_msg))}")
                    else:
                        raise Exception(f"NVIDIA API Error: {error_msg}")
                else:
                    raise Exception(f"Unexpected API response format: {result}")
            
            return result["choices"][0]["message"]["content"]
            
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
