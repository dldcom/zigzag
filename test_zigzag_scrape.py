import requests
import json

urls = [
    "https://zigzag.kr/catalog/products/169495381?product_id=169495381&shop_id=17294&share_type=AFFILIATE&referral_code=DN5kAPme&zz_source=zz_affiliate&zz_campaign=DN5kAPme&airbridge_referrer=airbridge%3Dtrue%26client_id%3Df7c00baf-29b8-4a54-aee0-66afd33b1b2b%26event_uuid%3Dc7128f8c-d96d-417b-ae18-34e9bebedf08%26referrer_timestamp%3D1781073671313%26channel%3Daffiliate&utm_source=affiliate",
    "https://zigzag.kr/catalog/products/170061617?product_id=170061617&shop_id=35995&share_type=AFFILIATE&referral_code=DN5kAPme&zz_source=zz_affiliate&zz_campaign=DN5kAPme&airbridge_referrer=airbridge%3Dtrue%26client_id%3Df7c00baf-29b8-4a54-aee0-66afd33b1b2b%26event_uuid%3D5c4e9f95-8696-4798-b06c-7c00f2cf0ef8%26referrer_timestamp%3D1781073687721%26channel%3Daffiliate&utm_source=affiliate",
    "https://zigzag.kr/catalog/products/157732173?product_id=157732173&shop_id=4431&share_type=AFFILIATE&referral_code=DN5kAPme&zz_source=zz_affiliate&zz_campaign=DN5kAPme&airbridge_referrer=airbridge%3Dtrue%26client_id%3Df7c00baf-29b8-4a54-aee0-66afd33b1b2b%26event_uuid%3Df098db68-e110-42ec-81f0-6b6783075e14%26referrer_timestamp%3D1781073699464%26channel%3Daffiliate&utm_source=affiliate"
]

results = []
for url in urls:
    try:
        resp = requests.post('http://127.0.0.1:5000/api/fetch_product', json={'url': url})
        results.append(resp.json())
    except Exception as e:
        results.append({'error': str(e)})

with open('zigzag_output.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Zigzag scraping completed.")
