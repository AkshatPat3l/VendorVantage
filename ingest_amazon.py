import os
import requests
from db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

def harvest_amazon_by_term(term):
    api_key = os.getenv("RAINFOREST_API_KEY")
    params = {
        'api_key': api_key,
        'type': 'search',
        'amazon_domain': 'amazon.ca',
        'search_term': term
    }
    
    print("Connecting to Rainforest API...")
    try:
        response = requests.get('https://api.rainforestapi.com/request', params)
        response.raise_for_status()
        items = response.json().get('search_results', [])

        conn = get_db_connection()
        cur = conn.cursor()

        for item in items:
            asin = item.get('asin')
            title = item.get('title')
            brand = item.get('brand', 'Amazon Vendor')
            price = item.get('price', {}).get('value', 0.00)
            rating = item.get('rating', 0.0)

            # 1. Update Core Product
            cur.execute("""
                INSERT INTO products (id, title, price, brand, rating)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET price = EXCLUDED.price, rating = EXCLUDED.rating;
            """, (asin, title, price, brand, rating))

            # 2. Log Price History
            cur.execute("INSERT INTO price_history (product_id, price) VALUES (%s, %s)", (asin, price))

            # 3. Update Inventory (Randomized for demo)
            cur.execute("""
                INSERT INTO inventory (product_id, stock_level)
                VALUES (%s, floor(random() * 100 + 1)::int)
                ON CONFLICT DO NOTHING;
            """, (asin,))

        conn.commit()
        cur.close()
        conn.close()
        print(f"Success! {len(items)} products synced with History & Inventory.")
        return len(items)

    except Exception as e:
        print(f"Sync Error: {e}")
        return 0

if __name__ == "__main__":
    harvest_amazon_by_term('smart home')