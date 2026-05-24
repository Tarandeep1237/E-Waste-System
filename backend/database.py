import mysql.connector
from mysql.connector import pooling
import logging
from config import Config

logger = logging.getLogger(__name__)

# Global connection pool
db_pool = None

def init_db_pool():
    """Initialize the MySQL connection pool."""
    global db_pool
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="ewaste_pool",
            pool_size=5,
            pool_reset_session=True,
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            autocommit=True
        )
        logger.info("MySQL Connection Pool initialized successfully.")
    except mysql.connector.Error as err:
        logger.error(f"Error initializing MySQL Pool: {err}")
        # Let it fail gracefully or retry in production, for now just raise
        raise

def get_db_connection():
    """Get a connection from the pool."""
    global db_pool
    if db_pool is None:
        init_db_pool()
    return db_pool.get_connection()

def setup_schema():
    """Create necessary tables if they don't exist."""
    conn = None
    try:
        # Connect without DB first to create the DB if it doesn't exist
        temp_conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        temp_cursor.close()
        temp_conn.close()

        # Now connect with DB
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('user', 'admin') DEFAULT 'user',
                points_balance INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')

        # 2. Bookings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                image_url TEXT NOT NULL,
                category VARCHAR(100) NOT NULL,
                confidence_score FLOAT NOT NULL,
                status ENUM('pending', 'scheduled', 'collected', 'rejected') DEFAULT 'pending',
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                address TEXT NOT NULL,
                scheduled_date DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # 3. Rewards Transactions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rewards (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                booking_id VARCHAR(36),
                points INT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL
            )
        ''')
        
        logger.info("Database schema setup complete.")
    except Exception as e:
        logger.error(f"Failed to setup schema: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
