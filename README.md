# Servicio web: PDF a texto (Python)

## Requisitos
- Python 3.10+

## Instalacion
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoint
- `POST /extract-text`
- `multipart/form-data`
- campo: `file` (PDF)

Respuesta:
```json
{
  "filename": "documento.pdf",
  "pages": 3,
  "text": "...texto extraido...",
  "plazo": 12,
  "defectos": ["B07G", "B08G"]
}
```

`plazo`:
- numero entero si encuentra `en el plazo maximo de X meses`
- `NOT_FOUND` si no encuentra el patron

`defectos`:
- array con los codigos encontrados en el texto del PDF
- los codigos se cargan desde `app/defect_codes.txt` (uno por linea)
- se ignoran lineas vacias o que empiezan por `#`

## Prueba rapida con curl
```bash
curl -X POST "http://127.0.0.1:8000/extract-text" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@C:/ruta/documento.pdf"
```

## Salud del servicio
- `GET /health`
