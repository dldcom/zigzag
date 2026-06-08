from bs4 import BeautifulSoup
import json

file_path = r"C:\Users\dldco\.gemini\antigravity\brain\7bb50fbc-ca66-4611-9a88-c486cde5e472\.system_generated\steps\111\content.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

title = soup.title.string if soup.title else "Not found"
price_meta = soup.find("meta", property="product:price:amount") or soup.find("meta", property="og:price:amount")
price = price_meta["content"] if price_meta else "Not found"

brand = "NAMED COLLECTIVE" # Default based on domain

# Let's see if there are any JSON-LD scripts with product info
for script in soup.find_all('script', type='application/ld+json'):
    try:
        data = json.loads(script.string)
        if isinstance(data, list):
            data = data[0]
        if data.get('@type') == 'Product':
            brand_info = data.get('brand', {})
            if isinstance(brand_info, dict):
                brand = brand_info.get('name', brand)
            else:
                brand = brand_info
            
            offers = data.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0]
            if isinstance(offers, dict) and 'price' in offers:
                price = str(offers['price'])
    except:
        pass

print(f"Brand: {brand}")
print(f"Title: {title.strip()}")
print(f"Price: {price}")
