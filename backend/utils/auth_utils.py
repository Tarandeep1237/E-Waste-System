import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import Config
from database import get_db_connection

def generate_token(user_id, role):
    """Generate a JWT token valid for 24 hours."""
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'role': role
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def token_required(f):
    """Decorator to protect routes requiring authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
            
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = get_user_by_id(data['sub'])
            if not current_user:
                return jsonify({'error': 'Invalid user token!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to protect routes requiring admin privileges."""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin privileges required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def get_user_by_id(user_id):
    """Helper to fetch a user from DB by ID."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, role, points_balance FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
