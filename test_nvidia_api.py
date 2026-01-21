import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Accept": "application/json"
}

payload = {
    "model": "google/gemma-3-27b-it",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 512,
    "temperature": 0.20,
    "top_p": 0.70,
    "stream": False
}

print("Testing NVIDIA API...")
print(f"URL: {invoke_url}")
print(f"Model: {payload['model']}")
print(f"API Key (first 10 chars): {NVIDIA_API_KEY[:10]}...")
print("\nSending request...\n")

try:
    response = requests.post(invoke_url, headers=headers, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\nResponse Body:")
    print(response.text)
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"\nParsed JSON:")
            print(json.dumps(result, indent=2))
            
            if "choices" in result:
                print(f"\n✓ Success! Response: {result['choices'][0]['message']['content']}")
            else:
                print(f"\n✗ Error: 'choices' key not found in response")
        except json.JSONDecodeError as e:
            print(f"\n✗ Failed to parse JSON: {e}")
    else:
        print(f"\n✗ Request failed with status {response.status_code}")
        
except Exception as e:
    print(f"\n✗ Exception: {e}")
    import traceback
    traceback.print_exc()
