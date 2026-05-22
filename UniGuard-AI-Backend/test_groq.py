import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Loaded API Key: {api_key}")

if api_key:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
else:
    print("API Key is missing/None!")
