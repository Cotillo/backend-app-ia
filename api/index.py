from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, storage
import os


app = FastAPI()

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")  # Asegurate de tener este archivo en la raíz del proyecto
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'dat-in-69b46.appspot.com'  # Cambia esto por el bucket de tu Firebase
    })

@app.get("/")
async def root():
    return JSONResponse(content={"message": "¡Backend IA activo y funcionando!"})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        bucket = storage.bucket()
        blob = bucket.blob(file.filename)
        blob.upload_from_string(contents, content_type=file.content_type)
        url = blob.public_url

return {
    "message": f"Archivo '{file.filename}' subido correctamente.",
    "firebase_url": url
}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
