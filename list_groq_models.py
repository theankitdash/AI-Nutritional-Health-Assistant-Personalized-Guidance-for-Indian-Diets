import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("✗ Error: GROQ_API_KEY not found in .env")
    exit(1)

url = "https://api.groq.com/openai/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print(f"Fetching active models from Groq (API Key: {api_key[:10]}...)...")

try:
    response = httpx.get(url, headers=headers, timeout=15.0)
    if response.status_code == 200:
        data = response.json()
        models = [m["id"] for m in data.get("data", [])]
        print(f"\n✓ Found {len(models)} available models on your Groq account:\n")
        for m in sorted(models):
            print(f"  • {m}")
    else:
        print(f"\n✗ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"\n✗ Request failed: {e}")
