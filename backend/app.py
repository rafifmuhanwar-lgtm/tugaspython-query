import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Add the current directory to sys.path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from firebase_config import db
from matchmaking import join_queue_logic, get_dashboard_stats, get_user_matches_count

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'valorant_secret_key_super_secure'

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if db is None:
            flash('Error konfigurasi database Firebase. Hubungi admin.', 'danger')
            return render_template('login.html')

        users_ref = db.collection('users')
        query = users_ref.where('username', '==', username).stream()
        user_doc = next(query, None)
        
        if user_doc:
            user_data = user_doc.to_dict()
            if check_password_hash(user_data['password'], password):
                session['username'] = user_data['username']
                session['rank'] = user_data['rank']
                return redirect(url_for('dashboard'))
            else:
                flash('Password salah!', 'danger')
        else:
            flash('Username tidak ditemukan!', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rank = request.form['rank']
        
        if db is None:
            flash('Error konfigurasi database Firebase. Hubungi admin.', 'danger')
            return render_template('register.html')

        users_ref = db.collection('users')
        query = users_ref.where('username', '==', username).stream()
        if next(query, None):
            flash('Username sudah terdaftar!', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        users_ref.add({
            'username': username,
            'password': hashed_password,
            'rank': rank,
            'created_at': datetime.now().isoformat()
        })
        flash('Registrasi berhasil, silakan login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    stats = get_dashboard_stats() if db else {'total_users': 0, 'total_matches': 0, 'total_queue': 0, 'total_online': 0}
    return render_template('dashboard.html', username=session['username'], rank=session['rank'], stats=stats)

@app.route('/queue')
def queue():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('queue.html', username=session['username'])

@app.route('/join_queue', methods=['POST'])
def join_queue():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
    
    if db is None:
        return jsonify({'status': 'error', 'message': 'Firebase not configured'}), 500

    # Check if already in queue
    queue_ref = db.collection('queue')
    existing = list(queue_ref.where('username', '==', session['username']).where('status', '==', 'waiting').stream())
    if existing:
        return jsonify({'status': 'error', 'message': 'Anda sudah berada di dalam queue!'}), 400
        
    success, msg = join_queue_logic(session['username'], session['rank'])
    return jsonify({'status': 'success', 'message': msg})

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    matches = []
    if db:
        matches_ref = db.collection('matches').order_by('created_at', direction='DESCENDING').stream()
        matches = [m.to_dict() for m in matches_ref]
    
    return render_template('history.html', matches=matches)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    total_match = get_user_matches_count(session['username']) if db else 0
    
    # Dummy stats for Win Rate and KDA as requested
    profile_data = {
        'username': session['username'],
        'rank': session['rank'],
        'total_match': total_match,
        'win_rate': '54.2%',
        'kda': '1.85'
    }
    return render_template('profile.html', profile=profile_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
