import os
from flask import Flask, render_template, request, redirect, flash
from db import execute_query

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def handle_search():
    search_term = request.form.get('query')
    if not search_term:
        return redirect('/')

    # Import and trigger the harvester logic
    from ingest_amazon import harvest_amazon_by_term
    
    try:
        count = harvest_amazon_by_term(search_term)
        # flash(f"Success! Added {count} products for '{search_term}'") # Optional flash message
    except Exception as e:
        print(f"Search Ingest Error: {e}")

    return redirect('/')




@app.route('/')
def dashboard():
    # 1. Fetch the products with stock
    query = """
        SELECT p.*, COALESCE(i.stock_level, 0) as stock_level 
        FROM products p
        LEFT JOIN inventory i ON p.id = i.product_id
        ORDER BY p.price DESC;
    """
    products = execute_query(query) or []
    
    # 2. Calculate KPI Metrics
    total_value = sum(p['price'] * p['stock_level'] for p in products) if products else 0
    low_stock_count = sum(1 for p in products if p['stock_level'] < 20) if products else 0
    
    valid_ratings = [p['rating'] for p in products if p.get('rating') is not None]
    if valid_ratings:
        avg_rating = float(sum(valid_ratings) / len(valid_ratings))
    else:
        avg_rating = 0.0

    return render_template('index.html', 
                           products=products, 
                           total=len(products),
                           total_value=total_value,
                           low_stock=low_stock_count,
                           avg_rating=round(avg_rating, 1))
# Professional "Health" endpoint
@app.route('/health')
def health():
    return {"status": "healthy", "database": "connected"}, 200

if __name__ == "__main__":
    # Use environment port for deployment, default to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)