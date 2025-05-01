from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, storage
import os


app = FastAPI()

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        private_key_env = os.getenv("FIREBASE_PRIVATE_KEY")
if private_key_env is None:
    raise ValueError("FIREBASE_PRIVATE_KEY no está definida en las variables de entorno")

"private_key": private_key_env.replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    })
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
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
