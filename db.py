import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from psycopg2.extras import execute_values

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


def execute_batch_upsert(query, data_list):
    conn = get_db_connection()
    if not conn: 
        return
    try:
        cur = conn.cursor()
        # execute_values is 10x faster than a standard for-loop
        execute_values(cur, query, data_list)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Batch Error: {e}")