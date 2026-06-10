import os
import json
import html
import instaloader
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_file, send_from_directory
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

# Initialize Instaloader
L = instaloader.Instaloader(
    download_pictures=False,
    download_video_thumbnails=False,
    download_videos=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False
)

# Optional Login (uncomment or leave active based on requirements)
# username = os.environ.get("INSTAGRAM_USERNAME")
# password = os.environ.get("INSTAGRAM_PASSWORD")

# if username and password:
#     try:
#         L.login(username, password)
#         print(f"Successfully logged in as {username}")
#     except Exception as e:
#         print(f"Login failed: {e}")

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_post():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Extract shortcode
        shortcode = None
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0]
        else:
            return jsonify({'error': 'Invalid Instagram URL format'}), 400

        # Fetch post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        media_urls = []
        if post.typename == 'GraphSidecar':
            # Multiple media (carousel)
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    media_urls.append({'type': 'video', 'url': node.video_url})
                else:
                    media_urls.append({'type': 'image', 'url': node.display_url})
        elif post.is_video:
            # Single video
            media_urls.append({'type': 'video', 'url': post.video_url})
        else:
            # Single image
            media_urls.append({'type': 'image', 'url': post.url})

        return jsonify({'success': True, 'shortcode': shortcode, 'media': media_urls})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch_product', methods=['POST'])
def fetch_product():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    try:
        if 'musinsa.com' in url or '29cm' in url:
            from playwright.sync_api import sync_playwright
            import time
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
                page.goto(url, wait_until="networkidle")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2) # Wait for lazy loaded images
                html_content = page.content()
                browser.close()
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            import cloudscraper
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, headers=headers, timeout=10)
            html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. 텍스트 정보 추출
        og_title = soup.find('meta', property='og:title')
        title = og_title['content'].strip() if og_title else (soup.title.string.strip() if soup.title else "Unknown Product")
        
        import re
        title = re.sub(r'\s+', ' ', title) # Clean up newlines and extra spaces
        title = re.split(r'\s+[-|]\s+', title)[0].strip() # Remove " - 사이트명" or " | 사이트명"

        brand = "Unknown Brand"
        
        # 무신사 등 한국 쇼핑몰: "브랜드명(영문) 제품명" 형태 분리
        m = re.match(r'^(\S+(?:\([^)]+\))?)\s+(.*)$', title)
        if m and ('musinsa' in url or '29cm' in url):
            brand = m.group(1).strip()
            title = m.group(2).strip()
        
        price_tag = soup.find('meta', property='product:price:amount') or soup.find('meta', property='og:price:amount')
        currency_tag = soup.find('meta', property='product:price:currency') or soup.find('meta', property='og:price:currency')
        
        if price_tag:
            currency = currency_tag['content'] if currency_tag else ""
            p_val = price_tag['content'].replace(',', '').split('.')[0]
            try:
                formatted_price = f"{int(p_val):,}"
            except:
                formatted_price = p_val
            price = f"{currency} {formatted_price}".strip()
        else:
            price = "Price not found"

        og_desc = soup.find('meta', property='og:description')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = ""
        if og_desc and og_desc.get('content'):
            description = og_desc['content'].strip()
        elif meta_desc and meta_desc.get('content'):
            description = meta_desc['content'].strip()

        image_urls = []
        
        # 2. JSON-LD 파싱
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                ld_data = json.loads(script.string)
                if isinstance(ld_data, list):
                    ld_data = ld_data[0]
                    
                if ld_data.get('@type') == 'Product':
                    brand_info = ld_data.get('brand', {})
                    if isinstance(brand_info, dict) and 'name' in brand_info:
                        brand = brand_info['name']
                    elif isinstance(brand_info, str):
                        brand = brand_info
                        
                    if ld_data.get('description'):
                        description = str(ld_data['description']).strip()
                        
                    imgs = ld_data.get('image', [])
                    if isinstance(imgs, list):
                        image_urls.extend(imgs)
                    elif isinstance(imgs, str):
                        image_urls.append(imgs)
            except Exception:
                continue
                
        # 3. Fallback & Site-specific Logic
        if 'musinsa.com' in url:
            # Musinsa images
            import re
            m_urls = re.findall(r'https://image\.msscdn\.net/[^\x22\x27\s\?]+\.jpg', html_content)
            product_id = url.split('products/')[1].split('?')[0] if 'products/' in url else ''
            
            for u in set(m_urls):
                # 0. 메인 썸네일 갤러리 사진들만 추출 (항상 _500.jpg로 로딩됨)
                if '_500.jpg' not in u:
                    continue
                    
                # 1. 리뷰/코디 사진 제외
                if 'review' in u.lower() or 'estimate' in u.lower() or 'snap' in u.lower():
                    continue
                
                # 2. 다른 상품 추천 사진(goods_img) 제외 (현재 상품 ID와 일치해야 함)
                if product_id and product_id not in u:
                    continue
                    
                # 3. 고화질 이미지 URL로 변환 (본문 prd_img와 동일 사이즈)
                u = u.replace('/thumbnails/', '/')
                u = u.replace('_500.jpg', '_big.jpg')
                
                if u not in image_urls:
                    image_urls.append(u)

        if not image_urls:
            og_image = soup.find('meta', property='og:image')
            if og_image:
                image_urls.append(og_image['content'])
                
        # URL 특수문자 해제 및 완성
        media_urls = []
        for img_url in image_urls:
            img_url = html.unescape(img_url)
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            media_urls.append({'type': 'image', 'url': img_url})

        return jsonify({
            'success': True,
            'is_product': True,
            'brand': brand,
            'title': title,
            'price': price,
            'description': description,
            'media': media_urls
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_media():
    data = request.json
    url = data.get('url')
    filename = data.get('filename', 'downloaded_media.jpg')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Send file to client
        file_obj = BytesIO(response.content)
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=filename,
            mimetype=response.headers.get('Content-Type', 'image/jpeg')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview', methods=['GET'])
def preview_media():
    url = request.args.get('url')
    if not url:
        return "URL is required", 400

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        file_obj = BytesIO(response.content)
        return send_file(
            file_obj,
            mimetype=response.headers.get('Content-Type', 'image/jpeg')
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
