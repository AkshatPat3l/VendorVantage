import os
from flask import Flask, render_template, request, redirect
from db import execute_query

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/search', methods=['POST'])
def handle_search():
    search_term = request.form.get('query')
    if not search_term:
        return redirect('/')

    # This now hits the GraphQL Home Depot engine
    from ingest_homedepot import harvest_homedepot_by_term
    try:
        harvest_homedepot_by_term(search_term, total_target=500)
    except Exception as e:
        print(f"Home Depot Ingest Error: {e}")

    return redirect('/')

@app.route('/')
def dashboard():
    # Fetch all HD products and their stock
    query = """
        SELECT p.*, COALESCE(i.stock_level, 0) as stock_level 
        FROM products p
        LEFT JOIN inventory i ON p.id = i.product_id
        WHERE p.price > 0
        ORDER BY p.price DESC;
    """
    products = execute_query(query) or []
    
    # Metrics
    total_value = sum(p['price'] * p['stock_level'] for p in products)
    low_stock = sum(1 for p in products if p['stock_level'] < 20)
    
    valid_ratings = [p['rating'] for p in products if p['rating'] > 0]
    avg_rating = round(sum(valid_ratings) / len(valid_ratings), 1) if valid_ratings else 0.0

    return render_template('index.html', 
                           products=products, 
                           total=len(products),
                           total_value=total_value,
                           low_stock=low_stock,
                           avg_rating=avg_rating)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))