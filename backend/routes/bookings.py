from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required
from database import get_db_connection
from utils.rewards_utils import calculate_reward_points
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
            SELECT b.id, b.image_url, b.category, b.confidence_score, b.status, 
                   b.latitude, b.longitude, b.address, b.scheduled_date, b.created_at,
                   r.points as points_awarded
            FROM bookings b
            LEFT JOIN rewards r ON b.id = r.booking_id
            WHERE b.user_id = %s 
            ORDER BY b.created_at DESC
        ''', (current_user['id'],))
        
        bookings = cursor.fetchall()
        
        # Format datetimes and calculate dynamic reward points
        for b in bookings:
            b['scheduled_date'] = b['scheduled_date'].isoformat() if b['scheduled_date'] else None
            b['created_at'] = b['created_at'].isoformat() if b['created_at'] else None
            
            # If collected, use actual points awarded. Otherwise, calculate estimate based on availability.
            if b['points_awarded'] is not None:
                b['points'] = b['points_awarded']
            else:
                b['points'] = calculate_reward_points(b['category'], conn)
                
            # Clean up temporary field
            del b['points_awarded']
            
        return jsonify({"bookings": bookings}), 200
        
    except Exception as e:
        logger.error(f"Booking history error: {e}")
        return jsonify({"error": "Failed to fetch bookings"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@bookings_bp.route('/<booking_id>', methods=['DELETE'])
@token_required
def delete_booking(current_user, booking_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if booking exists
        cursor.execute("SELECT user_id, status FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
            
        # Admins can delete any booking; users can only delete their own
        if current_user['role'] != 'admin' and booking['user_id'] != current_user['id']:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Fetch any reward associated with this booking
        cursor.execute("SELECT points, user_id FROM rewards WHERE booking_id = %s", (booking_id,))
        reward = cursor.fetchone()
        
        if reward:
            # Revert user points balance
            cursor.execute(
                "UPDATE users SET points_balance = GREATEST(0, points_balance - %s) WHERE id = %s",
                (reward['points'], reward['user_id'])
            )
            # Delete reward transaction
            cursor.execute("DELETE FROM rewards WHERE booking_id = %s", (booking_id,))
            
        # Delete booking from database
        cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
        conn.commit()
        
        return jsonify({"message": "Booking deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Booking deletion error: {e}")
        return jsonify({"error": "Failed to delete booking"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



