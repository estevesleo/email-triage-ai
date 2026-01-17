from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.utils.extract_text import extract_text_from_upload
from app.services.llm import classify_and_reply
from app.utils.heuristics import heuristic_fallback

app = FastAPI(title="Email Triage AI")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "error": None})

@app.post("/process", response_class=HTMLResponse)
async def process_email(
    request: Request,
    email_text: str = Form(default=""),
    file: UploadFile | None = File(default=None),
):
    try:
        text = email_text.strip()

        if file and file.filename:
            extracted = await extract_text_from_upload(file)
            text = (text + "\n\n" + extracted).strip() if text else extracted.strip()

        if not text:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "result": None,
                "error": "Envie um arquivo (.txt/.pdf) ou cole o texto do email."
            })

        # IA (principal)
        try:
            result = classify_and_reply(text)
        except Exception:
            # fallback (não deixa o app “morrer” no demo)
            result = heuristic_fallback(text)

        return templates.TemplateResponse("index.html", {"request": request, "result": result, "error": None})

    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": None,
            "error": f"Erro ao processar: {str(e)}"
        })
