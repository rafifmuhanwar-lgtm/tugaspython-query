import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            # Coba ambil dari Environment Variable (untuk Deployment Vercel/Render)
            firebase_cred_env = os.environ.get('FIREBASE_CREDENTIALS')
            
            if firebase_cred_env:
                cred_dict = json.loads(firebase_cred_env)
                cred = credentials.Certificate(cred_dict)
            else:
                # Fallback ke file lokal jika Environment Variable tidak ada
                cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
                cred = credentials.Certificate(cred_path)
                
            firebase_admin.initialize_app(cred)
            print("Firebase Admin terhubung dengan sukses!")
        except Exception as e:
            print(f"===========================================================")
            print(f"ERROR FIREBASE: {e}")
            print(f"Pastikan kamu sudah set Environment Variable FIREBASE_CREDENTIALS di server deployment")
            print(f"Atau letakkan file 'serviceAccountKey.json' secara lokal di dalam folder backend/")
            print(f"===========================================================")
            return None
    return firestore.client()

db = initialize_firebase()
