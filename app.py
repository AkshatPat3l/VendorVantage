import os
import psycopg2
from flask import Flask, render_template
from psycopg2.extras import RealDictCursor
from db import get_db_connection

app = Flask(__name__)
app.secret_key = os.urandom(24)

def execute_relational_query(query, params=None):
    """
    Standardizes database access using RealDictCursor.
    This allows p['price'] access in Python and p.price in Jinja.
    """
    conn = get_db_connection()
    # FIX: Corrected cursor initialization to avoid TypeError
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()

@app.route('/')
def dashboard():
    # 1. ANALYTICS QUERY (JOINING DIMENSIONS & FACTS)
    # Using a Window Function to calculate brand average in a single pass
    query = """
        SELECT 
            p.product_id, 
            p.title, 
            p.photo_url, 
            p.category,
            b.brand_name, 
            s.price, 
            s.rating,
            AVG(s.price) OVER(PARTITION BY b.brand_id) as brand_avg_price
        FROM dim_products p
        JOIN dim_brands b ON p.brand_id = b.brand_id
        JOIN fact_inventory_snapshots s ON p.product_id = s.product_id
        WHERE s.sync_date = (
            SELECT MAX(sync_date) 
            FROM fact_inventory_snapshots 
            WHERE product_id = p.product_id
        )
        ORDER BY s.price DESC;
    """
    products = execute_relational_query(query)

    # 2. CALCULATE SUPPLIER INTELLIGENCE (MARKET SHARE)
    total_market_value = sum(float(p['price']) for p in products) if products else 0
    
    brand_stats = {}
    for p in products:
        name = p['brand_name']
        if name not in brand_stats:
            brand_stats[name] = {'value': 0, 'count': 0}
        brand_stats[name]['value'] += float(p['price'])
        brand_stats[name]['count'] += 1

    # Format for Chart.js and Sidebar
    brands_data = []
    for name, stats in brand_stats.items():
        share = (stats['value'] / total_market_value * 100) if total_market_value > 0 else 0
        brands_data.append({
            'brand_name': name,
            'share': round(share, 1),
            'count': stats['count'],
            'total_value': stats['value']
        })

    # Sort brands by market share for the chart
    brands_data = sorted(brands_data, key=lambda x: x['share'], reverse=True)

    # 3. KPI SUMMARY
    avg_rating = 0
    if products:
        valid_ratings = [float(p['rating']) for p in products if p['rating'] > 0]
        avg_rating = round(sum(valid_ratings) / len(valid_ratings), 1) if valid_ratings else 0

    return render_template('index.html', 
                           products=products, 
                           brands=brands_data,
                           total_value=total_market_value,
                           total_count=len(products),
                           avg_rating=avg_rating,
                           system_status="GCP-TOR-ZONE-1: ACTIVE")

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)