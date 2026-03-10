import os
import requests
import time
from db import execute_batch_upsert
from dotenv import load_dotenv

load_dotenv()

def harvest_500_diverse_step_by_step():
    API_KEY = os.getenv("SERP_API_KEY")
    
    # 5 Departments x 100 items each = 500 total
    departments = ["Appliances", "Power Tools", "Grills", "Kitchen", "Smart Home"]
    
    product_batch = []
    processed_ids = set()
    
    print(f"🚀 INITIATING BALANCED 500-ITEM SWEEP...")

    for dept in departments:
        dept_captured = 0
        print(f"\n📂 CATEGORY: {dept}")
        
        # We need approx 4-5 pages to get 100 unique items per dept
        for page_num in range(1, 6):
            if dept_captured >= 100: break
            
            print(f"   📄 Page {page_num}: Fetching DNA...", end="\r")
            
            params = {
                "engine": "home_depot",
                "q": dept,
                "api_key": API_KEY,
                "page": str(page_num),
                "ps": "24" 
            }

            try:
                res = requests.get("https://serpapi.com/search", params=params, timeout=30)
                data = res.json()
                items = data.get("products", [])
                
                if not items: break

                for item in items:
                    if dept_captured >= 100: break
                    
                    pid = str(item.get("product_id"))
                    if not pid or pid in processed_ids:
                        continue
                    
                    # --- TYPE-SAFE PRICE EXTRACTION ---
                    price_data = item.get("price")
                    if isinstance(price_data, dict):
                        price = float(price_data.get("value", 0))
                    else:
                        price = float(price_data or 0)

                    brand = (item.get("brand") or dept).upper()
                    title = item.get("title", "Unknown").upper()
                    thumb = item.get("thumbnails", [[""]])[0][0]

                    product_batch.append((
                        pid, title[:255], price, brand, 
                        item.get("rating", 4.5), thumb
                    ))
                    processed_ids.add(pid)
                    dept_captured += 1

                print(f"   ✅ Page {page_num} Synced. [Dept Total: {dept_captured}/100]")
                time.sleep(1) 

            except Exception as e:
                print(f"\n   ❌ Error in {dept}: {e}")
                break
        
        print(f"🏁 Department '{dept}' locked with {dept_captured} products.")

    if product_batch:
        print(f"\n💾 FINAL SYNC: Injecting {len(product_batch)} items into Supabase...")
        execute_batch_upsert("""
            INSERT INTO products (id, title, price, brand, rating, photo_url)
            VALUES %s ON CONFLICT (id) DO UPDATE SET price = EXCLUDED.price;
        """, product_batch)
        print("🎉 INVENTORY SYNC COMPLETE. 500 Unique SKUs locked.")

if __name__ == "__main__":
    harvest_500_diverse_step_by_step()