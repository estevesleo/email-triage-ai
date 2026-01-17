import os
import json


import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  

def classify_and_reply(email_text: str) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não configurada.")

    prompt = f"""
Você é um assistente de triagem de emails.
Classifique o email como: "Produtivo" ou "Improdutivo".
Depois sugira uma resposta curta e profissional em português.

Responda APENAS em JSON com as chaves:
{{
  "category": "Produtivo|Improdutivo",
  "confidence": 0-1,
  "suggested_reply": "texto",
  "reason": "1 frase curta"
}}

EMAIL:
\"\"\"{email_text}\"\"\"
""".strip()

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "Responda somente em JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]

    # Tenta parsear JSON robustamente
    data = json.loads(content)
    return data
