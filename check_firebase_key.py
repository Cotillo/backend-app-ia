import json
import os

def validate_firebase_key(file_path="firebase-key.json"):
    required_fields = [
        "type", "project_id", "private_key_id", "private_key",
        "client_email", "client_id", "auth_uri", "token_uri",
        "auth_provider_x509_cert_url", "client_x509_cert_url"
    ]

    if not os.path.exists(file_path):
        print("❌ Error: El archivo firebase-key.json no se encuentra.")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("❌ Error: El archivo no es un JSON válido.")
            return False

    missing = [field for field in required_fields if field not in data]
    if missing:
        print(f"❌ Faltan los siguientes campos en firebase-key.json: {missing}")
        return False

    if "\\n" not in data["private_key"]:
        print("❌ Error: El campo 'private_key' no está escapado correctamente con '\\\\n'.")
        print("💡 Solución: asegurate de no copiarlo manualmente ni abrirlo con un editor que reemplace los saltos.")
        return False

    print("✅ firebase-key.json es válido y está correctamente formateado.")
    return True

if __name__ == "__main__":
    validate_firebase_key()
