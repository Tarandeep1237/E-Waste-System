from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required
from database import get_db_connection
import uuid
import logging

logger = logging.getLogger(__name__)
bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/create', methods=['POST'])
@token_required
def create(current_user):
    data = request.get_json()
    
    required_fields = ['image_url', 'category', 'confidence_score', 'latitude', 'longitude', 'address', 'scheduled_date']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        booking_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO bookings (id, user_id, image_url, category, confidence_score, latitude, longitude, address, scheduled_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            booking_id,
            current_user['id'],
            data['image_url'],
            data['category'],
            data['confidence_score'],
            data['latitude'],
            data['longitude'],
            data['address'],
            data['scheduled_date']
        ))
        
        conn.commit()
        
        return jsonify({"message": "Booking created successfully", "booking_id": booking_id}), 201
        
    except Exception as e:
        logger.error(f"Booking creation error: {e}")
        return jsonify({"error": "Failed to create booking"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@bookings_bp.route('/history', methods=['GET'])
@token_required
def history(current_user):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT id, image_url, category, confidence_score, status, latitude, longitude, address, scheduled_date, created_at 
            FROM bookings 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (current_user['id'],))
        
        bookings = cursor.fetchall()
        
        # Format datetimes for JSON serialization
        for b in bookings:
            b['scheduled_date'] = b['scheduled_date'].isoformat() if b['scheduled_date'] else None
            b['created_at'] = b['created_at'].isoformat() if b['created_at'] else None
            
        return jsonify({"bookings": bookings}), 200
        
    except Exception as e:
        logger.error(f"Booking history error: {e}")
        return jsonify({"error": "Failed to fetch bookings"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
