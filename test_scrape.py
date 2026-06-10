import requests
import json

urls = [
    "https://namedcollective.com/products/midnight-studded-off-the-shoulder-sweater-camo?variant=56997075976573&zappid=1",
    "https://www.musinsa.com/products/5573822"
]

results = []
for url in urls:
    try:
        resp = requests.post('http://127.0.0.1:5000/api/fetch_product', json={'url': url})
        results.append(resp.json())
    except Exception as e:
        results.append({'error': str(e)})

with open('scraper_output.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Scraping completed.")
