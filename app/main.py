from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.utils.extract_text import extract_text_from_upload
from app.services.llm import classify_and_reply
from app.utils.heuristics import heuristic_fallback

app = FastAPI(title="Email Triage AI")
templates = Jinja2Templates(directory="app/templates")

# Ajuste: limiar para decidir se vale chamar IA
HEURISTIC_CONFIDENCE_THRESHOLD = 0.85


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": None, "error": None},
    )


@app.post("/process", response_class=HTMLResponse)
async def process_email(
    request: Request,
    email_text: str = Form(default=""),
    file: UploadFile | None = File(default=None),
):
    print("PROCESS: start", flush=True)

    try:
        text = (email_text or "").strip()
        print(f"PROCESS: initial text length={len(text)}", flush=True)

        if file and file.filename:
            print(
                f"PROCESS: file received name='{file.filename}' content_type='{file.content_type}'",
                flush=True,
            )

            extracted = await extract_text_from_upload(file)
            extracted = (extracted or "").strip()
            print(f"PROCESS: extracted length={len(extracted)}", flush=True)

            if extracted:
                text = (text + "\n\n" + extracted).strip() if text else extracted

        print(f"PROCESS: final merged text length={len(text)}", flush=True)

        if not text:
            print("PROCESS: empty text -> returning validation error", flush=True)
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "result": None,
                    "error": "Envie um arquivo (.txt/.pdf) ou cole o texto do email.",
                },
            )

        # 1) Heurística primeiro (rápida e barata)
        heur = heuristic_fallback(text)
        heur_conf = float(heur.get("confidence", 0.0))
        print(f"PROCESS: heuristic confidence={heur_conf}", flush=True)

        # 2) Se heurística estiver segura, NÃO chama OpenAI
        if heur_conf >= HEURISTIC_CONFIDENCE_THRESHOLD:
            print("PROCESS: using heuristic result (skip OpenAI)", flush=True)
            result = heur
        else:
            # 3) Caso incerto, tenta OpenAI. Se falhar (ex. 429), usa heurística.
            try:
                print("PROCESS: calling classify_and_reply (OpenAI)", flush=True)
                result = classify_and_reply(text)
                print("PROCESS: OpenAI OK", flush=True)
            except Exception as e:
                print("PROCESS: OpenAI FAILED -> fallback to heuristic. Error:", repr(e), flush=True)
                result = heur

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": result, "error": None},
        )

    except Exception as e:
        print("PROCESS: unexpected exception:", repr(e), flush=True)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": None, "error": f"Erro ao processar: {str(e)}"},
        )
