import os
from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()

PORT = int(os.getenv("PORT",9000))
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRES_HOURS",24))
COLLECTION = os.getenv("FIRESTORE_COLLECTION_USUARIO", "usuarios_python")

db = firestore.Client(project=PROJECT_ID)
