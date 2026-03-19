import re
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pypdf import PdfReader

app = FastAPI(title="PDF Text Extractor API", version="1.0.0")
PLAZO_NOT_FOUND = "NOT_FOUND"
PLAZO_PATTERN = re.compile(r"en\s+el\s+plazo\s+m[aá]ximo\s+de\s+(\d+)\s+mes(?:es)?", re.IGNORECASE)
DEFECT_CODES_FILE = Path(__file__).with_name("defect_codes.txt")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def extract_plazo(text: str) -> int | str:
    match = PLAZO_PATTERN.search(text)
    if not match:
        return PLAZO_NOT_FOUND
    return int(match.group(1))


def load_defect_codes(file_path: Path) -> list[str]:
    if not file_path.exists():
        return []

    codes: list[str] = []
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        code = raw_line.strip().upper()
        if not code or code.startswith("#"):
            continue
        codes.append(code)
    return codes


DEFECT_CODES = load_defect_codes(DEFECT_CODES_FILE)
DEFECT_CODES_PATTERN = (
    re.compile(r"\b(?:{})\b".format("|".join(re.escape(code) for code in DEFECT_CODES)), re.IGNORECASE)
    if DEFECT_CODES
    else None
)


def extract_defectos(text: str) -> list[str]:
    if DEFECT_CODES_PATTERN is None:
        return []

    found_codes: list[str] = []
    seen: set[str] = set()
    for match in DEFECT_CODES_PATTERN.finditer(text):
        code = match.group(0).upper()
        if code in seen:
            continue
        seen.add(code)
        found_codes.append(code)
    return found_codes


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
        "defectos": extract_defectos(full_text),
    }
