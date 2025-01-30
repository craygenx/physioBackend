import firebase_admin
from firebase_admin import credentials, firestore, auth
import os


FIREBASE_CREDENTIALS_PATH = "/etc/secrets/firebase_credentials.json"

if not os.path.exists(FIREBASE_CREDENTIALS_PATH):raise ValueError('firebase credentials file not found')
# Load Firebase credentials
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
