import os
from flask import Flask, render_template
from db import execute_query

app = Flask(__name__)

@app.route('/')
def dashboard():
    # COALESCE ensures that if stock_level is NULL, it returns 0 instead
    query = """
        SELECT p.*, COALESCE(i.stock_level, 0) as stock_level 
        FROM products p
        LEFT JOIN inventory i ON p.id = i.product_id
        ORDER BY p.price DESC;
    """
    data = execute_query(query)
    count = len(data) if data else 0
    return render_template('index.html', products=data, total=count)
# Professional "Health" endpoint
@app.route('/health')
def health():
    return {"status": "healthy", "database": "connected"}, 200

if __name__ == "__main__":
    # Use environment port for deployment, default to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)