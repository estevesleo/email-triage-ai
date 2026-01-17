import io
import pdfplumber

async def extract_text_from_upload(file):
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages)

    raise ValueError("Formato não suportado. Envie .txt ou .pdf.")
