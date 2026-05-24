from flask import Blueprint, request, jsonify
from utils.auth_utils import admin_required
from database import get_db_connection
from route_opt.route_opt import nearest_neighbor_tsp
import uuid
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard(current_admin):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Base Stats
        cursor.execute("SELECT COUNT(*) as total FROM bookings WHERE status = 'collected'")
        total_pickups = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM bookings WHERE status IN ('pending', 'scheduled')")
        pending_approvals = cursor.fetchone()['pending']
        
        cursor.execute("SELECT SUM(points) as total_points FROM rewards WHERE points > 0")
        points_row = cursor.fetchone()
        points_distributed = points_row['total_points'] if points_row['total_points'] else 0
        
        # 2. Category Analytics
        cursor.execute("SELECT category, COUNT(*) as count FROM bookings GROUP BY category")
        category_rows = cursor.fetchall()
        category_stats = {row['category']: row['count'] for row in category_rows}
        
        # 3. All Bookings (with User details)
        cursor.execute('''
            SELECT b.id, b.image_url, b.category, b.confidence_score, b.status, 
                   b.latitude, b.longitude, b.address, b.scheduled_date, 
                   b.user_id, u.name as user_name, u.email as user_email
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            ORDER BY b.created_at DESC
        ''')
        bookings = cursor.fetchall()
        
        for b in bookings:
            b['scheduled_date'] = b['scheduled_date'].isoformat() if b['scheduled_date'] else None

        return jsonify({
            "stats": {
                "totalPickups": total_pickups,
                "pendingApprovals": pending_approvals,
                "pointsDistributed": int(points_distributed)
            },
            "categoryStats": category_stats,
            "bookings": bookings
        }), 200

    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        return jsonify({"error": "Failed to fetch dashboard data"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@admin_bp.route('/optimize-routes', methods=['POST'])
@admin_required
def optimize_routes(current_admin):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch pending/scheduled bookings
        cursor.execute("SELECT id, latitude as lat, longitude as lng FROM bookings WHERE status IN ('pending', 'scheduled')")
        locations = cursor.fetchall()
        
        if not locations:
            return jsonify({"route_coords": []}), 200
            
        # Optimize
        # Default start coord could be the depot (e.g. New Delhi central)
        depot_coord = (28.6139, 77.2090) 
        optimized_route = nearest_neighbor_tsp(locations, depot_coord)
        
        return jsonify({"route_coords": optimized_route}), 200
        
    except Exception as e:
        logger.error(f"Route optimization error: {e}")
        return jsonify({"error": "Failed to optimize route"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@admin_bp.route('/bookings/<booking_id>/status', methods=['PUT'])
@admin_required
def update_booking_status(current_admin, booking_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['scheduled', 'collected', 'rejected']:
        return jsonify({"error": "Invalid status"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check current booking
        cursor.execute("SELECT user_id, status FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
            
        if booking['status'] == new_status:
            return jsonify({"message": "Status unchanged"}), 200

        # Update status
        cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", (new_status, booking_id))
        
        # If collected, award points
        if new_status == 'collected' and booking['status'] != 'collected':
            points_to_award = 50  # Arbitrary points calculation
            reward_id = str(uuid.uuid4())
            
            # Insert reward transaction
            cursor.execute('''
                INSERT INTO rewards (id, user_id, booking_id, points, description)
                VALUES (%s, %s, %s, %s, %s)
            ''', (reward_id, booking['user_id'], booking_id, points_to_award, "Points for e-waste collection"))
            
            # Update user balance
            cursor.execute('''
                UPDATE users SET points_balance = points_balance + %s WHERE id = %s
            ''', (points_to_award, booking['user_id']))

        return jsonify({"message": f"Booking updated to {new_status}"}), 200

    except Exception as e:
        logger.error(f"Status update error: {e}")
        return jsonify({"error": "Failed to update status"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
