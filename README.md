# Universal Grabber (Instagram & Shopping Mall Image Extractor)

## 📌 개요
**Universal Grabber**는 인스타그램 게시물 및 다양한 쇼핑몰(Named Collective, 무신사 등)의 제품 사진과 정보를 버튼 클릭 한 번으로 손쉽게 추출하고 다운로드할 수 있는 만능 웹 애플리케이션입니다.
어떤 링크를 넣든 프로그램이 자동으로 **인스타그램인지 쇼핑몰인지 감지(Auto-detect)**하여 맞춤형 스크래핑을 진행합니다.

## ✨ 주요 기능

### 1. 인스타그램 스크래핑 (Instagram)
- 인스타그램 게시물 링크를 입력하면 게시물에 포함된 **모든 사진(여러 장 포함)**을 고화질로 추출합니다.
- 사진 하단에 원본 출처(게시자 계정명)를 표시하며, 클릭 한 번으로 사진을 압축(ZIP)하여 다운로드할 수 있습니다.

### 2. 글로벌 쇼핑몰 스크래핑 (Shopify 기반 - Named Collective 등)
- 해외 쇼핑몰 링크 입력 시, 웹페이지에 숨겨져 있는 **JSON-LD(구조화된 데이터)**를 파싱합니다.
- **브랜드명, 제품명, 가격(통화 포함)**을 정확히 추출하고, 고화질 썸네일 갤러리를 불러옵니다.

### 3. 한국형 복합 쇼핑몰 스크래핑 (무신사 특화)
- 최신 웹 기술(React SPA)과 Lazy Loading이 적용된 **무신사(Musinsa)**의 이미지를 완벽하게 긁어옵니다.
- **가상 브라우저(Playwright)**를 띄워 스크롤을 맨 밑까지 내려 자바스크립트 로딩을 유도합니다.
- 지저분한 리뷰 사진, 추천 상품, 세로로 긴 본문 상세 설명 사진은 모두 필터링합니다.
- 오직 **'상단 메인 제품 사진(갤러리 썸네일)'**만을 골라내어 고화질(`_big.jpg`)로 자동 변환해 보여줍니다.
- 가격에 콤마(,) 표시 및 불필요한 제품명 뒷부분(`- 사이즈 & 후기`)을 깔끔하게 제거합니다.

## 🛠️ 기술 스택
- **Backend:** Python 3, Flask
- **Scraping & Parsing:**
  - `BeautifulSoup4`: HTML 및 Meta 태그 파싱
  - `cloudscraper`: Cloudflare 봇 방어(우회) 및 기본 HTTP 요청
  - `playwright`: 가상 브라우저 제어 (무신사 등 동적 로딩 SPA 사이트 대응)
- **Frontend:** HTML5, Vanilla CSS, Vanilla JavaScript

## 🚀 설치 및 실행 방법

1. **라이브러리 설치**
   ```bash
   pip install flask requests beautifulsoup4 cloudscraper playwright
   playwright install chromium
   ```

2. **서버 실행**
   ```bash
   python app.py
   ```

3. **웹 접속**
   브라우저를 열고 `http://127.0.0.1:5000` 으로 접속합니다.
   원하는 링크를 복사하여 입력창에 넣고 `FETCH` 버튼을 클릭합니다.

## 📝 특이 사항 (Troubleshooting)
- **Cloudflare 차단 우회**: 무신사 등의 사이트는 일반 `requests` 사용 시 `Attention Required! | Cloudflare` 봇 차단 화면이 뜹니다. 이를 우회하기 위해 `cloudscraper`를 도입했습니다.
- **무신사 Playwright 도입**: 무신사는 첫 접속 시 HTML에 제품 상세 사진이 들어있지 않고 자바스크립트로 로딩됩니다. 따라서 백엔드에서 `playwright` 헤드리스 브라우저를 띄워 스크롤을 내려 이미지를 동적으로 불러오도록 설계되었습니다. (처리 시간 3~5초 소요)
- **이미지 자동 다운로드 보안 정책**: 최신 브라우저에서는 CORS(교차 출처 리소스 공유) 정책으로 인해 외부 서버 사진을 캔버스로 직접 다운로드하는 것이 막혀 있습니다. 이를 해결하기 위해 Flask 백엔드에 이미지 프록시(Proxy) API `/api/preview`와 일괄 다운로드 API `/api/download`를 만들어 자체 서버를 경유하도록 설계했습니다.
