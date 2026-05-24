from flask import Blueprint, jsonify
from utils.auth_utils import token_required
from database import get_db_connection
import logging

logger = logging.getLogger(__name__)
rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/balance', methods=['GET'])
@token_required
def balance(current_user):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get balance from users table (already cached)
        cursor.execute("SELECT points_balance FROM users WHERE id = %s", (current_user['id'],))
        user_row = cursor.fetchone()
        
        # Get transaction history
        cursor.execute('''
            SELECT id, booking_id, points, description, created_at 
            FROM rewards 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (current_user['id'],))
        history = cursor.fetchall()
        
        for h in history:
            h['created_at'] = h['created_at'].isoformat() if h['created_at'] else None
            
        return jsonify({
            "balance": user_row['points_balance'] if user_row else 0,
            "history": history
        }), 200
        
    except Exception as e:
        logger.error(f"Rewards balance error: {e}")
        return jsonify({"error": "Failed to fetch rewards"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
