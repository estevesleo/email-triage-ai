import os
import json
import re
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def classify_and_reply(email_text: str) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não configurada.")

    prompt = f"""
Você é um assistente de triagem de emails para uma empresa do setor financeiro.

Classifique o email como "Produtivo" ou "Improdutivo" e gere uma resposta curta e profissional.

Regras:
- Se for Produtivo e NÃO houver identificador (nº de chamado/protocolo/requisição), peça esse identificador.
- Não invente prazos, números ou promessas.

Responda APENAS em JSON válido, sem texto extra, com as chaves:
{{
  "category": "Produtivo|Improdutivo",
  "confidence": 0.0-1.0,
  "suggested_reply": "texto",
  "reason": "1 frase curta"
}}

EMAIL:
\"\"\"{email_text}\"\"\"
""".strip()

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "Responda SOMENTE com JSON válido. Sem markdown. Sem texto antes/depois."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        # Se der erro HTTP, printa o corpo pra você ver no log
        if r.status_code >= 400:
            print("OpenAI HTTP error:", r.status_code, r.text[:1000])
            r.raise_for_status()

        content = r.json()["choices"][0]["message"]["content"]
        print("OpenAI raw content (first 400 chars):", content[:400])

        # Parse robusto: extrai o primeiro JSON que aparecer
        match = re.search(r"\{.*\}", content, re.S)
        if not match:
            raise ValueError("Resposta da IA não contém JSON.")

        data = json.loads(match.group(0))
        return data

    except Exception as e:
        print("OpenAI classify_and_reply exception:", repr(e))
        raise
