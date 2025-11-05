import mysql.connector

def setup_database():
    """Create database and tables if they don't exist"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database = "urdu_search_engine"
        )
        
        return conn
        
    except Error as e:
        print(f"Error setting up database: {e}")
        return None