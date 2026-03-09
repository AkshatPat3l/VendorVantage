import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        # Strip potential quotes from Render/Docker env vars
        raw_db_url = os.getenv("DATABASE_URL")
        if not raw_db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        db_url = raw_db_url.strip().replace('"', '').replace("'", "")
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return None    

def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn: return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        results = cur.fetchall() if cur.description else None
        conn.commit()
        cur.close()
        conn.close()
        return results
    except Exception as e: 
        print(f"Query Error: {e}")
        return None