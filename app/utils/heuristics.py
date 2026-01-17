import re

def heuristic_fallback(text: str) -> dict:
    t = text.lower()

    improd = any(k in t for k in ["feliz natal", "parabéns", "obrigado", "agradeço", "bom dia", "boa tarde"])
    produt = any(k in t for k in ["status", "prazo", "requisição", "protocolo", "chamado", "anexo", "erro", "ajuda"])

    if produt and not improd:
        return {
            "category": "Produtivo",
            "confidence": 0.55,
            "suggested_reply": "Olá! Recebido. Pode me informar o número da requisição/chamado para eu verificar o status e retornar com uma atualização?",
            "reason": "Contém termos de solicitação/status."
        }

    return {
        "category": "Improdutivo",
        "confidence": 0.55,
        "suggested_reply": "Olá! Muito obrigado pela mensagem. Fico à disposição caso precise de suporte.",
        "reason": "Não indica ação imediata."
    }

