from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, storage
import os

app = FastAPI()

# Cargar clave segura desde variables
private_key_env = os.getenv("FIREBASE_PRIVATE_KEY")

if private_key_env is None:
    raise ValueError("FIREBASE_PRIVATE_KEY no está definida en las variables de entorno")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": private_key_env.replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    })
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
    })

@app.get("/")
async def root():
    return JSONResponse(content={"message": "¡Backend IA activo y funcionando con ENV!"})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()

        bucket = storage.bucket()
        blob = bucket.blob(filename)
        blob.upload_from_string(contents, content_type=file.content_type)
        url = blob.public_url

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        if ext == ".csv":
            df = pd.read_csv(tmp_path)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(tmp_path)
        elif ext == ".json":
            df = pd.read_json(tmp_path)
        else:
            return JSONResponse(content={"error": f"Formato no soportado: {ext}"}, status_code=400)

        variables = []
        for col in df.columns:
            tipo = "numérico" if pd.api.types.is_numeric_dtype(df[col]) else \
                   "fecha" if pd.api.types.is_datetime64_any_dtype(df[col]) else \
                   "booleano" if pd.api.types.is_bool_dtype(df[col]) else \
                   "categórico" if df[col].nunique() < len(df[col]) / 2 else \
                   "texto libre"

            pregunta = f"¿La columna '{col}' representa un valor de tipo {tipo}?"
            cuadro = tipo == "fecha"
            variables.append({
                "nombre": col,
                "tipo_sugerido": tipo,
                "pregunta": pregunta,
                "cuadro_selector_rango": cuadro
            })

        return {
            "message": f"Archivo '{filename}' subido correctamente.",
            "firebase_url": url,
            "variables": variables
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/confirm-selection")
async def confirmar_variables(payload: dict):
    try:
        archivo = payload.get("nombre_archivo")
        confirmaciones = payload.get("confirmaciones", [])
        if not archivo or not confirmaciones:
            return JSONResponse(status_code=400, content={"error": "Faltan campos obligatorios"})

        db = firestore.client()
        db.collection("definiciones").document(archivo).set({"confirmaciones": confirmaciones})
        return {"message": "Confirmaciones guardadas exitosamente"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-dashboard")
async def generate_dashboard(nombre_archivo: str):
    try:
        db = firestore.client()
        doc = db.collection("definiciones").document(nombre_archivo).get()
        if not doc.exists:
            return JSONResponse(status_code=404, content={"error": "No se encontraron confirmaciones para ese archivo"})

        definiciones = doc.to_dict().get("confirmaciones", [])
        bucket = storage.bucket()
        blob = bucket.blob(nombre_archivo)
        ext = os.path.splitext(nombre_archivo)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            blob.download_to_filename(tmp.name)
            tmp_path = tmp.name

        if ext == ".csv":
            df = pd.read_csv(tmp_path)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(tmp_path)
        elif ext == ".json":
            df = pd.read_json(tmp_path)
        else:
            return JSONResponse(content={"error": f"Formato no soportado: {ext}"}, status_code=400)

        widgets = generar_dash_por_variables(df, definiciones)

        return {
            "dashboard_url": None,
            "widgets": widgets
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
