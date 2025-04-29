from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, storage
import os
from .schemas import ConfirmVariablesResponse, VariableSuggestion
import csv
import io


app = FastAPI()

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    path = os.path.join(os.path.dirname(__file__), "..", "firebase-key.json")
    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'dat-in-69b46.firebasestorage.app'
    })

@app.get("/")
async def root():
    return JSONResponse(content={"message": "¡Backend IA activo y funcionando en Vercel!"})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename

    # Subir archivo a Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_string(content, content_type=file.content_type)

    url = blob.public_url

    return {
        "message": f"Archivo '{filename}' subido correctamente a Firebase Storage.",
        "firebase_url": url
    }
@app.post("/confirm-variables", response_model=ConfirmVariablesResponse)
async def confirm_variables(filename: str):
    # Descarga temporal desde Firebase
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    content = blob.download_as_text()

    # Leer archivo CSV
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    suggestions = []

    if not rows:
        return ConfirmVariablesResponse(variables=[])

    sample_row = rows[0]

    for column, value in sample_row.items():
        if value is None:
            tipo = "texto"
        else:
            try:
                float(value)
                tipo = "numérico"
            except ValueError:
                if "-" in value or "/" in value:
                    tipo = "fecha"
                elif value.lower() in ["true", "false", "yes", "no", "si", "no"]:
                    tipo = "booleano"
                elif len(value) < 20:
                    tipo = "categórico"
                else:
                    tipo = "texto"

        suggestions.append(VariableSuggestion(nombre=column, tipo_sugerido=tipo))

    return ConfirmVariablesResponse(variables=suggestions)
