from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
import sqlite3
import json
import os
import hashlib
import secrets

from py_backend import (
    backend_init, backend_add_city, backend_add_road,
    backend_shortest_path_json, backend_graph_json,
    backend_allocate_resources, backend_add_request
)

app = Flask(__name__, static_folder='../frontend', static_url_path='/static')
app.secret_key = secrets.token_hex(32)
CORS(app)

# ─── Database ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'disaster_relief.db')


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY,
        name TEXT,
        population INTEGER,
        damage_level INTEGER,
        resources INTEGER,
        latitude REAL,
        longitude REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS roads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        src INTEGER,
        dest INTEGER,
        distance INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER,
        priority INTEGER,
        required_resources INTEGER,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ─── Initialize ─────────────────────────────────────────────────────────────
backend_init()
init_db()


def restore_state():
    conn = get_db()
    c = conn.cursor()

    c.execute('SELECT * FROM cities ORDER BY id')
    for row in c.fetchall():
        backend_add_city(
            row['name'], row['population'], row['damage_level'],
            row['resources'], row['latitude'], row['longitude']
        )

    c.execute('SELECT * FROM roads')
    for row in c.fetchall():
        backend_add_road(row['src'], row['dest'], row['distance'])

    c.execute('SELECT * FROM requests WHERE status = ? ORDER BY id', ('pending',))
    for row in c.fetchall():
        backend_add_request(row['city_id'], row['priority'], row['required_resources'])

    conn.close()


restore_state()


# ─── Auth helpers ────────────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


# ─── Page routes ─────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    return app.send_static_file('index.html')


@app.route('/login')
def login_page():
    return app.send_static_file('login.html')


@app.route('/signup')
def signup_page():
    return app.send_static_file('signup.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return app.send_static_file('index.html')


@app.route('/cities')
@login_required
def cities_page():
    return app.send_static_file('cities.html')


@app.route('/roads')
@login_required
def roads_page():
    return app.send_static_file('roads.html')


@app.route('/requests')
@login_required
def requests_page():
    return app.send_static_file('requests.html')


@app.route('/allocate')
@login_required
def allocate_page():
    return app.send_static_file('allocate.html')


@app.route('/logs')
@login_required
def logs_page():
    return app.send_static_file('logs.html')


@app.route('/map')
@login_required
def map_page():
    return app.send_static_file('map.html')


@app.route('/emergency')
@login_required
def emergency_page():
    return app.send_static_file('emergency.html')


# ─── Auth API ────────────────────────────────────────────────────────────────
@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm_password', '')

    if not username or not email or not password:
        return redirect('/signup?error=All+fields+are+required')

    if password != confirm:
        return redirect('/signup?error=Passwords+do+not+match')

    if len(password) < 6:
        return redirect('/signup?error=Password+must+be+at+least+6+characters')

    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                     (username, email, hash_password(password)))
        conn.commit()
        conn.close()
        return redirect('/login?success=Account+created+successfully')
    except sqlite3.IntegrityError:
        conn.close()
        return redirect('/signup?error=Username+or+email+already+exists')


@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?',
                        (username, hash_password(password))).fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/')
    else:
        return redirect('/login?error=Invalid+username+or+password')


@app.route('/api/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/api/me', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'username': session['username']})
    return jsonify({'logged_in': False})


# ─── City API ────────────────────────────────────────────────────────────────
@app.route('/api/city/add', methods=['POST'])
@login_required
def add_city():
    data = request.json
    name = data['name']
    pop = data['population']
    damage = data['damage_level']
    res = data['resources']
    lat = data['latitude']
    lon = data['longitude']

    city_id = backend_add_city(name, pop, damage, res, lat, lon)

    conn = get_db()
    conn.execute('INSERT INTO cities VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (city_id, name, pop, damage, res, lat, lon))
    conn.execute('INSERT INTO logs (action, details) VALUES (?, ?)',
                 ('add_city', f'Added city: {name}'))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'id': city_id})


@app.route('/api/city/list', methods=['GET'])
@login_required
def list_cities():
    conn = get_db()
    rows = conn.execute('SELECT * FROM cities').fetchall()
    conn.close()
    return jsonify({'cities': [dict(row) for row in rows]})


# ─── Road API ────────────────────────────────────────────────────────────────
@app.route('/api/road/add', methods=['POST'])
@login_required
def add_road():
    data = request.json
    src = data['src']
    dest = data['dest']
    dist = data['distance']

    backend_add_road(src, dest, dist)

    conn = get_db()
    conn.execute('INSERT INTO roads (src, dest, distance) VALUES (?, ?, ?)',
                 (src, dest, dist))
    conn.execute('INSERT INTO logs (action, details) VALUES (?, ?)',
                 ('add_road', f'Added road: {src} -> {dest} ({dist} km)'))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/road/list', methods=['GET'])
@login_required
def list_roads():
    conn = get_db()
    rows = conn.execute('SELECT * FROM roads').fetchall()
    conn.close()
    return jsonify({'roads': [dict(row) for row in rows]})


# ─── Request API ─────────────────────────────────────────────────────────────
@app.route('/api/request/add', methods=['POST'])
@login_required
def add_request():
    data = request.json
    city_id = data['city_id']
    priority = data['priority']
    required = data['required_resources']

    try:
        conn = get_db()
        cursor = conn.execute(
            'INSERT INTO requests (city_id, priority, required_resources, status) VALUES (?, ?, ?, ?)',
            (city_id, priority, required, 'pending')
        )
        req_id = cursor.lastrowid
        conn.execute('INSERT INTO logs (action, details) VALUES (?, ?)',
                     ('add_request', f'Added disaster request #{req_id} for city {city_id}'))
        conn.commit()
        conn.close()

        backend_add_request(city_id, priority, required)

        return jsonify({'success': True, 'request_id': req_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/request/list', methods=['GET'])
@login_required
def list_requests():
    conn = get_db()
    rows = conn.execute('''
        SELECT r.id, r.city_id, c.name as city_name, r.priority,
               r.required_resources as required, r.status
        FROM requests r
        LEFT JOIN cities c ON r.city_id = c.id
        ORDER BY r.priority DESC
    ''').fetchall()
    conn.close()
    return jsonify({'requests': [dict(row) for row in rows]})


# ─── Allocation API ─────────────────────────────────────────────────────────
@app.route('/api/allocate', methods=['POST'])
@login_required
def allocate():
    try:
        result_json = backend_allocate_resources()
        result = json.loads(result_json)

        conn = get_db()
        for alloc in result['allocations']:
            if alloc['status'] == 'allocated':
                conn.execute('UPDATE requests SET status = ? WHERE id = ?',
                             ('allocated', alloc['request_id']))
                conn.execute('INSERT INTO logs (action, details) VALUES (?, ?)',
                             ('allocate', f"Allocated {alloc['allocated']} resources "
                              f"from {alloc['support_city']} to {alloc['affected_city']}"))
        conn.commit()
        conn.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'allocations': []}), 500


# ─── Logs API ────────────────────────────────────────────────────────────────
@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    conn = get_db()
    rows = conn.execute('SELECT * FROM logs ORDER BY created_at DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify({'logs': [dict(row) for row in rows]})


# ─── Graph / Shortest Path API ──────────────────────────────────────────────
@app.route('/api/graph-info', methods=['GET'])
@login_required
def graph_info():
    result_json = backend_graph_json()
    result = json.loads(result_json)
    return jsonify(result)


@app.route('/api/shortest-path', methods=['GET'])
@login_required
def shortest_path():
    src = int(request.args.get('src'))
    dest = int(request.args.get('dest'))

    result_json = backend_shortest_path_json(src, dest)
    result = json.loads(result_json)

    if result.get('success'):
        conn = get_db()
        conn.execute('INSERT INTO logs (action, details) VALUES (?, ?)',
                     ('shortest_path', f"Computed path from {src} to {dest}: {result['distance']} km"))
        conn.commit()
        conn.close()

    return jsonify(result)


# ─── Emergency Numbers API ──────────────────────────────────────────────────
@app.route('/api/emergency-numbers', methods=['GET'])
@login_required
def emergency_numbers():
    numbers = [
        {"name": "National Disaster Response Force (NDRF)", "number": "011-24363260", "category": "Disaster", "icon": "shield-alt"},
        {"name": "National Emergency Number", "number": "112", "category": "Emergency", "icon": "phone-alt"},
        {"name": "Police", "number": "100", "category": "Law Enforcement", "icon": "user-shield"},
        {"name": "Fire Brigade", "number": "101", "category": "Fire", "icon": "fire-extinguisher"},
        {"name": "Ambulance", "number": "102", "category": "Medical", "icon": "ambulance"},
        {"name": "Disaster Management (NDMA)", "number": "1078", "category": "Disaster", "icon": "house-damage"},
        {"name": "Women Helpline", "number": "1091", "category": "Safety", "icon": "female"},
        {"name": "Child Helpline", "number": "1098", "category": "Safety", "icon": "child"},
        {"name": "Road Accident Emergency", "number": "1073", "category": "Accident", "icon": "car-crash"},
        {"name": "Earthquake / Flood / Disaster", "number": "011-26701728", "category": "Disaster", "icon": "water"},
        {"name": "Indian Red Cross Society", "number": "011-23359379", "category": "Relief", "icon": "plus-square"},
        {"name": "Air Ambulance", "number": "9540161344", "category": "Medical", "icon": "helicopter"},
    ]
    return jsonify({'numbers': numbers})


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug_mode, port=5000)
