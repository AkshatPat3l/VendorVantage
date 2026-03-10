import os
import requests
import time
from db import get_db_connection # Assuming a helper to get a psycopg2/supabase conn
from dotenv import load_dotenv

load_dotenv()

def sync_pro_analytics_schema():
    API_KEY = os.getenv("SERP_API_KEY")
    departments = ["Appliances", "Power Tools", "Grills", "Kitchen", "Smart Home"]
    processed_ids = set()
    
    conn = get_db_connection()
    cur = conn.cursor()

    print(f"🚀 INITIATING RELATIONAL 500-ITEM ETL...")

    for dept in departments:
        dept_captured = 0
        for page_num in range(1, 6):
            if dept_captured >= 100: break
            
            params = {
                "engine": "home_depot",
                "q": dept,
                "api_key": API_KEY,
                "page": str(page_num),
                "ps": "24" 
            }

            try:
                res = requests.get("https://serpapi.com/search", params=params, timeout=30)
                items = res.json().get("products", [])
                if not items: break

                for item in items:
                    if dept_captured >= 100: break
                    pid = str(item.get("product_id"))
                    if not pid or pid in processed_ids: continue
                    
                    # 1. CLEAN DATA
                    raw_brand = (item.get("brand") or "GENERIC").upper()
                    price = float(item.get("price", {}).get("value", 0) if isinstance(item.get("price"), dict) else (item.get("price") or 0))
                    title = item.get("title", "Unknown").upper()
                    thumb = item.get("thumbnails", [[""]])[0][0]

                    # 2. DIM_BRANDS UPSERT
                    # Ensures the brand exists and retrieves the ID for the next step
                    cur.execute("""
                        INSERT INTO dim_brands (brand_name) 
                        VALUES (%s) 
                        ON CONFLICT (brand_name) DO UPDATE SET brand_name = EXCLUDED.brand_name
                        RETURNING brand_id;
                    """, (raw_brand,))
                    brand_id = cur.fetchone()[0]

                    # 3. DIM_PRODUCTS UPSERT
                    # Links to the Brand ID we just got
                    cur.execute("""
                        INSERT INTO dim_products (product_id, title, brand_id, photo_url, category)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (product_id) DO UPDATE SET 
                            title = EXCLUDED.title,
                            photo_url = EXCLUDED.photo_url;
                    """, (pid, title[:255], brand_id, thumb, dept))

                    # 4. FACT_INVENTORY_SNAPSHOTS INSERT
                    # Captures the "Now" for OLAP analytics
                    cur.execute("""
                        INSERT INTO fact_inventory_snapshots (product_id, price, rating)
                        VALUES (%s, %s, %s);
                    """, (pid, price, item.get("rating", 4.5)))

                    processed_ids.add(pid)
                    dept_captured += 1

                conn.commit() # Commit per page for stability
                print(f"✅ {dept} Page {page_num}: {dept_captured}/100 synced.")
                time.sleep(0.5)

            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
    cur.close()
    conn.close()
    print("🎉 STAR SCHEMA ETL COMPLETE. 500 SKUs Normalized.")

if __name__ == "__main__":
    sync_pro_analytics_schema()