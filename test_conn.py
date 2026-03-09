from db import execute_query

# This tries to read the 'products' table you made in the Supabase SQL editor
print("Testing VendorVantage connection...")
data = execute_query("SELECT * FROM products;")

if data is not None:
    print(f"Success! Database is live. Found {len(data)} rows.")
else:
    print("Connection failed. Check your .env file!")