import os
import requests
from db import execute_query
from dotenv import load_dotenv

load_dotenv()

def harvest_amazon():
    api_key = os.getenv("RAINFOREST_API_KEY")
    # Searching for Smart Home devices
    params = {
        'api_key': api_key,
        'type': 'search',
        'amazon_domain': 'amazon.ca', # Let's use Canada since you're in Toronto!
        'search_term': 'smart home'
    }
    
    print("Connecting to Rainforest API (Amazon Data)...")
    try:
        response = requests.get('https://api.rainforestapi.com/request', params)
        response.raise_for_status()
        data = response.json()
        
        # Rainforest returns results in 'search_results'
        items = data.get('search_results', [])

        for item in items:
            sku = item.get('asin') # Amazon uses ASIN as the unique identifier
            name = item.get('title')
            # Use 'brand' if available, otherwise 'Unknown'
            brand = item.get('brand', 'Amazon Vendor')
            category = "Smart Home"
            
            # Rainforest nested price structure
            price_data = item.get('price', {})
            price = price_data.get('value', 0.00)

            query = """
            INSERT INTO products (sku, name, brand, category, base_price)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (sku) DO UPDATE SET
                base_price = EXCLUDED.base_price;
            """
            execute_query(query, (sku, name, brand, category, price))
        
        print(f"Success! {len(items)} Amazon products synced to VendorVantage.")

    except Exception as e:
        print(f"Rainforest Sync Error: {e}")

if __name__ == "__main__":
    harvest_amazon()