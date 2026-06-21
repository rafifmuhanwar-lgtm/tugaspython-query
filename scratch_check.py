import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from backend.firebase_config import db

queue_ref = db.collection('queue').stream()
waiting = 0
print("--- QUEUE ---")
docs = list(queue_ref)
for doc in docs:
    data = doc.to_dict()
    print(f"ID: {doc.id}, Data: {data}")
    if data.get('status') == 'waiting':
        waiting += 1
print(f"Total waiting: {waiting}")

matches_ref = db.collection('matches').stream()
print("--- MATCHES ---")
matches = list(matches_ref)
for doc in matches:
    data = doc.to_dict()
    print(f"ID: {doc.id}, Match: {data.get('match_id')}")

# Jika nyangkut, hapus semua queue
if waiting > 0:
    print("Clearing queue...")
    for doc in docs:
        db.collection('queue').document(doc.id).delete()
    print("Queue cleared.")
