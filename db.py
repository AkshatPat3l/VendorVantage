import os;
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv();

def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"Error connecting to Supabase {e}")
        return None    

def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)

        results = None
        if cur.description:
            results = cur.fetchall()

        conn.commit()
        cur.close()
        conn.close()
        return results
    except Exception as e: 
        print (f"Query Error: {e}")
        return None

