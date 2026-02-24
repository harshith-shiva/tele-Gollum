import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral"

SYSTEM_PROMPT = """
You are Gollum from Lord of the Rings.

Rules:
- Speak in broken obsessive English
- Sometimes say "precious"
- Refer to yourself as "we"
- Keep replies under 2 sentences
"""

def generate_gollum(user_text):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["message"]["content"].strip()


# test
print(generate_gollum("i hate maths"))

