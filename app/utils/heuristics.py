import re

# Regex simples para pegar identificadores comuns:
# ex: "chamado 12345", "protocolo: 9876", "REQ-10293", "INC123456"
ID_PATTERNS = [
    re.compile(r"\b(chamado|protocolo|req|requisicao|requisição|ticket|inc)\s*[:#-]?\s*\d{3,}\b", re.I),
    re.compile(r"\b(REQ|INC|TKT|CASE)\s*[-#]?\s*\d{3,}\b", re.I),
    re.compile(r"\b\d{6,}\b"),  # números longos (último recurso)
]

IMPROD_KEYWORDS = [
    "feliz natal", "parabéns", "obrigado", "agradeço", "bom dia", "boa tarde", "boa noite",
    "feliz ano novo", "feliz aniversário", "valeu", "thanks", "thx"
]

PROD_KEYWORDS = [
    "status", "prazo", "requisição", "requisicao", "protocolo", "chamado", "ticket", "incidente",
    "anexo", "erro", "falha", "ajuda", "suporte", "atualização", "atualizacao", "pendente"
]


def _has_id(text: str) -> bool:
    for pat in ID_PATTERNS:
        if pat.search(text):
            return True
    return False


def _count_hits(t: str, keywords: list[str]) -> int:
    return sum(1 for k in keywords if k in t)


def heuristic_fallback(text: str) -> dict:
    t = (text or "").lower().strip()

    improd_hits = _count_hits(t, IMPROD_KEYWORDS)
    prod_hits = _count_hits(t, PROD_KEYWORDS)
    has_id = _has_id(text)

    # Casos bem claros: mensagem social/saudação
    if improd_hits >= 2 and prod_hits == 0:
        return {
            "category": "Improdutivo",
            "confidence": 0.92,
            "suggested_reply": "Olá! Obrigado pela mensagem. Qualquer coisa, fico à disposição.",
            "reason": "Mensagem social (saudação/agradecimento) sem solicitação."
        }

    # Casos bem claros: solicitação com ID
    if prod_hits >= 2 and has_id:
        return {
            "category": "Produtivo",
            "confidence": 0.90,
            "suggested_reply": "Olá! Recebido. Vou verificar o status da solicitação pelo ID informado e retorno com uma atualização em breve.",
            "reason": "Solicitação clara com identificador."
        }

    # Solicitação clara, mas sem ID -> pedir ID
    if prod_hits >= 2 and not has_id and improd_hits == 0:
        return {
            "category": "Produtivo",
            "confidence": 0.86,
            "suggested_reply": "Olá! Recebido. Para eu verificar e te atualizar, pode informar o número do chamado/protocolo/requisição?",
            "reason": "Solicitação clara de status/suporte sem identificador."
        }

    # Ambíguo: tem um pouco dos dois ou pouco sinal
    if prod_hits > 0 and improd_hits > 0:
        return {
            "category": "Produtivo",
            "confidence": 0.55,
            "suggested_reply": "Olá! Obrigado pela mensagem. Para eu te ajudar, poderia detalhar o que precisa e, se houver, enviar o número do chamado/protocolo?",
            "reason": "Conteúdo misto (social + possível demanda)."
        }

    # Poucos sinais produtivos
    if prod_hits == 1:
        # Se aparece um único termo produtivo, ainda pode ser demanda, mas com baixa confiança
        return {
            "category": "Produtivo",
            "confidence": 0.60,
            "suggested_reply": "Olá! Recebido. Pode detalhar melhor a solicitação e informar o número do chamado/protocolo, se houver?",
            "reason": "Indício leve de demanda."
        }

    # Default: improdutivo com confiança moderada
    return {
        "category": "Improdutivo",
        "confidence": 0.70,
        "suggested_reply": "Olá! Obrigado pela mensagem. Fico à disposição caso precise de suporte.",
        "reason": "Não há sinais claros de ação imediata."
    }
