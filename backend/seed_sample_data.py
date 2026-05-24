import uuid
import bcrypt
import logging
from database import setup_schema, get_db_connection
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_admin():
    """Seed a default admin user if one doesn't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id FROM users WHERE email = 'admin123@gmail.com'")
        if not cursor.fetchone():
            admin_id = str(uuid.uuid4())
            # bcrypt hash
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw('admin123'.encode('utf-8'), salt).decode('utf-8')
            
            cursor.execute('''
                INSERT INTO users (id, name, email, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', (admin_id, 'Super Admin', 'admin123@gmail.com', hashed, 'admin'))
            logger.info("Default admin created: admin123@gmail.com / admin123")
        else:
            logger.info("Admin user already exists.")
            
    except Exception as e:
        logger.error(f"Error seeding admin: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    logger.info("Starting database setup...")
    setup_schema()
    seed_admin()
    logger.info("Database setup complete.")
