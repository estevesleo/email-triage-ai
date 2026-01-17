# Email Triage AI (Produtivo vs Improdutivo)

Aplicação web simples para **classificar emails** como **Produtivo** ou **Improdutivo** e **sugerir uma resposta automática** com base no conteúdo.

## ✅ Funcionalidades
- Upload de email em `.txt` ou `.pdf`
- Ou colar o texto do email diretamente
- Classificação: **Produtivo** / **Improdutivo**
- Resposta sugerida (padrão e profissional)
- Exibe confiança e um motivo curto
- Fallback heurístico caso a API de IA esteja indisponível

---

## 🧱 Tecnologias
- Python + FastAPI
- Jinja2 (templates HTML)
- pdfplumber (leitura de PDF)
- Integração com API de IA (OpenAI) via HTTP

---

## 🚀 Como rodar localmente

### 1) Pré-requisitos
- Python 3.10+ (recomendado 3.11)
- (Opcional) Git

### 2) Clonar o repositório
```bash
git clone https://github.com/estevesleo/email-triage-ai.git
cd email-triage-ai
