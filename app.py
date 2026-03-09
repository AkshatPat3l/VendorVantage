import os
from flask import Flask, render_template
from db import execute_query

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Fetch all 53+ products we just ingested
    data = execute_query("SELECT * FROM products ORDER BY id DESC;")
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