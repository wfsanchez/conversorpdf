import re
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from pypdf import PdfReader

app = FastAPI(title="PDF Text Extractor API", version="1.0.0")
PLAZO_NOT_FOUND = "NOT_FOUND"
PLAZO_PATTERN = re.compile(r"en\s+el\s+plazo\s+m[aá]ximo\s+de\s+(\d+)\s+mes(?:es)?", re.IGNORECASE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def extract_plazo(text: str) -> int | str:
    match = PLAZO_PATTERN.search(text)
    if not match:
        return PLAZO_NOT_FOUND
    return int(match.group(1))


@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)) -> dict[str, object]:
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="El archivo esta vacio.")

    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="No se pudo leer el PDF.") from exc

    page_texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        page_texts.append(text)

    full_text = "\n".join(page_texts).strip()

    return {
        "filename": file.filename,
        "pages": len(reader.pages),
        "text": full_text,
        "plazo": extract_plazo(full_text),
    }
