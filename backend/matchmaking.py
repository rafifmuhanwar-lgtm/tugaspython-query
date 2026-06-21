from firebase_config import db
from datetime import datetime
import uuid

def join_queue_logic(username, rank):
    queue_ref = db.collection('queue')
    queue_ref.add({
        'username': username,
        'rank': rank,
        'join_time': datetime.now().isoformat(),
        'status': 'waiting'
    })

    # Trigger FIFO logic
    waiting_players = queue_ref.where('status', '==', 'waiting').order_by('join_time').limit(4).stream()
    players = []
    docs = []
    for doc in waiting_players:
        players.append(doc.to_dict())
        docs.append(doc.id)

    # Cek jika sudah mencapai 4 player (FIFO)
    if len(players) >= 4:
        team_a = players[:2]
        team_b = players[2:4]

        match_data = {
            'match_id': str(uuid.uuid4())[:8].upper(),
            'team_a': [p['username'] for p in team_a],
            'team_b': [p['username'] for p in team_b],
            'created_at': datetime.now().isoformat(),
            'status': 'finished'
        }

        # Simpan ke Match History
        db.collection('matches').add(match_data)

        # Hapus player dari Queue yang sudah masuk match
        for doc_id in docs[:4]:
            queue_ref.document(doc_id).delete()
        
        return True, "Match Created!"
    
    return False, "Joined Queue"

def get_dashboard_stats():
    # Menghitung data secara manual (untuk kompatibilitas library)
    users = len(list(db.collection('users').stream()))
    matches = len(list(db.collection('matches').stream()))
    queue = len(list(db.collection('queue').where('status', '==', 'waiting').stream()))
    
    return {
        'total_users': users,
        'total_matches': matches,
        'total_queue': queue,
        'total_online': min(users, 45) # Data dummy visual berdasarkan user terdaftar
    }

def get_user_matches_count(username):
    # Mengambil semua match dan filter berdasarkan username
    matches = db.collection('matches').stream()
    count = 0
    for m in matches:
        data = m.to_dict()
        if username in data.get('team_a', []) or username in data.get('team_b', []):
            count += 1
    return count
