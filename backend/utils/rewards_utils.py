import logging

logger = logging.getLogger(__name__)

def calculate_reward_points(category, conn=None):
    """
    Calculate reward points for a given e-waste category.
    Includes a base value and scales it dynamically based on the frequency
    of that category in the database (scarcity).
    """
    # Base points based on intrinsic rarity/value
    base_points = {
        'Laptop': 150,
        'Printer/Scanner': 120,
        'Smartphone': 100,
        'Display/Monitor': 80,
        'Keyboard/Mouse': 40,
        'Battery': 30,
        'Cables/Wires': 20
    }
    
    points = base_points.get(category, 50)
    
    # Dynamic adjustment based on current database availability
    # (High availability = common = lower rewards, Low availability = rare = higher rewards)
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Count total bookings
            cursor.execute("SELECT COUNT(*) as total FROM bookings")
            total_count = cursor.fetchone()['total']
            
            if total_count > 0:
                # Count current category bookings
                cursor.execute("SELECT COUNT(*) as cat_count FROM bookings WHERE category = %s", (category,))
                cat_count = cursor.fetchone()['cat_count']
                
                ratio = cat_count / total_count
                
                # If this category makes up more than 30% of all e-waste, reward goes down (multiplier 0.8)
                if ratio > 0.30:
                    points = int(points * 0.8)
                # If this category makes up less than 10% of all e-waste, reward goes up (multiplier 1.2)
                elif ratio < 0.10:
                    points = int(points * 1.2)
            cursor.close()
        except Exception as e:
            logger.error(f"Error calculating dynamic reward points: {e}")
            
    return max(10, points) # Keep a minimum of 10 points
