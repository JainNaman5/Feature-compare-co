# #Original code
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# from bs4 import BeautifulSoup
# import logging


# app = Flask(__name__)



# CORS(app)

# # Logging setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Common selectors for scraping
# PRICE_SELECTORS = ['.price', '.cost', '[class*="price"]', '[id*="price"]']
# DESC_SELECTORS = ['.description', '.product-description', '[class*="description"]']

# HEADERS = {
#     'User-Agent': (
#         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#         'AppleWebKit/537.36 (KHTML, like Gecko) '
#         'Chrome/91.0.4472.124 Safari/537.36'
#     )
# }

# def is_valid_url(url):
#     return url.startswith(('http://', 'https://'))

# def extract_text(soup, selectors, label, truncate=200):
#     for selector in selectors:
#         element = soup.select_one(selector)
#         if element:
#             return element.get_text(strip=True)[:truncate] + "..."
#     return None

# def scrape_features(url):
#     try:
#         logger.info(f"Scraping: {url}")
#         response = requests.get(url, headers=HEADERS, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')

#         features = {}

#         # Title
#         title = soup.find('h1')
#         if title:
#             features['Product'] = title.get_text(strip=True)

#         # Price
#         price = extract_text(soup, PRICE_SELECTORS, 'Price')
#         if price:
#             features['Price'] = price

#         # Description
#         description = extract_text(soup, DESC_SELECTORS, 'Description')
#         if not description:
#             meta = soup.find('meta', attrs={'name': 'description'})
#             content = meta.get('content', '') if meta else None
#             if isinstance(content, str):
#                 description = content[:200] + "..."
#             else:
#                 description = "No description found"
#         features['Description'] = description

#         # Feature lists
#         if len(features) <= 1:
#             import bs4
#             for i, ul in enumerate(soup.find_all(['ul', 'ol'])[:3]):
#                 if isinstance(ul, bs4.element.Tag):
#                     items = [li.get_text(strip=True) for li in ul.find_all('li')[:5]]
#                     if items:
#                         features[f'Feature List {i+1}'] = ', '.join(items)

#         # Fallback
#         if not features:
#             page_title = soup.find('title')
#             features = {
#                 'Title': page_title.get_text(strip=True) if page_title else 'No title found',
#                 'URL': url,
#                 'Content Length': f"{len(response.content)} bytes"
#             }

#         logger.info(f"Scraped {len(features)} features from {url}")
#         return features

#     except requests.RequestException as e:
#         logger.error(f"Request error: {e}")
#         return {'error': f'Failed to fetch {url}: {str(e)}'}
#     except Exception as e:
#         logger.error(f"Scraping error: {e}")
#         return {'error': f'Error scraping {url}: {str(e)}'}

# @app.route('/compare', methods=['POST'])
# def compare():
#     data = request.get_json()
#     if not data:
#         return jsonify({'error': 'Missing JSON payload'}), 400

#     url1, url2 = data.get('url1'), data.get('url2')
#     if not (url1 and url2):
#         return jsonify({'error': 'Both URLs are required'}), 400
#     if not (is_valid_url(url1) and is_valid_url(url2)):
#         return jsonify({'error': 'URLs must start with http:// or https://'}), 400

#     logger.info(f"Comparing: {url1} vs {url2}")
#     result1, result2 = scrape_features(url1), scrape_features(url2)

#     if 'error' in result1:
#         return jsonify({'error': result1['error']}), 400
#     if 'error' in result2:
#         return jsonify({'error': result2['error']}), 400

#     return jsonify({'data1': result1, 'data2': result2})

# @app.route('/health')
# def health_check():
#     return jsonify({'status': 'healthy'})

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({
#         'name': 'Universal Feature Comparator API',
#         'version': '1.1.0',
#         'endpoints': {
#             '/compare': 'POST - Compare features from two URLs',
#             '/health': 'GET - Health check'
#         }
#     })



# @app.route('/meta')
# def meta():
#     return jsonify({
#         "endpoints": {
#             "compare": "POST - Compare features from two URLs",
#             "health": "GET - Health check"
#         },
#         "name": "Universal Feature Comparator API",
#         "version": "1.0.0"
#     })



from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
# Import Playwright for robust, dynamic content scraping
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Playwright-based Scraping Functions ---

def is_valid_url(url):
    """Checks if the URL starts with http:// or https://."""
    return url.startswith(('http://', 'https://'))

def normalize_key(key):
    """
    Standardizes common feature names to ensure comparison consistency 
    (e.g., 'Memory' and 'RAM' both become 'RAM').
    """
    key = key.lower().replace('.', '').strip()
    mapping = {
        'memory': 'RAM',
        'ram': 'RAM',
        'internal storage': 'Storage',
        'storage': 'Storage',
        'battery capacity': 'Battery',
        'battery': 'Battery',
        'camera': 'Camera',
        'main camera': 'Camera',
        'display': 'Display',
        'screen size': 'Display',
        'price': 'Price',
        'product': 'Product',
        'description': 'Description'
    }
    
    # Check for substring matches
    for k, v in mapping.items():
        if k in key:
            return v
    
    return key.title()

def scrape_features(url):
    """
    Scrapes features using Playwright for dynamic rendering. 
    It contains specific selectors for Amazon and Flipkart.
    """
    data = {}
    try:
        logger.info(f"Scraping: {url}")
        with sync_playwright() as p:
            # Launch headless browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Use a longer timeout for e-commerce sites
            page.goto(url, timeout=45000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000) # Give extra time for JS to render

            # --- AMAZON Scraping Logic ---
            if 'amazon' in url:
                data['Source'] = 'Amazon'
                title = page.query_selector('#productTitle')
                # Try multiple price selectors common on Amazon
                price = page.query_selector('.a-price .a-offscreen') or page.query_selector('#priceblock_ourprice')
                
                # Tech Specs table
                specs_rows = page.query_selector_all('#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr')
                
                # Product Description (using the meta tag as a fallback for consistency)
                description_el = page.query_selector('meta[name="description"]')
                description_content = description_el.get_attribute('content') if description_el else None
                data['Description'] = (description_content[:200] + "...") if description_content and isinstance(description_content, str) else 'No description found'

                data['Product'] = title.inner_text().strip() if title else 'N/A'
                data['Price'] = price.inner_text().strip() if price else 'N/A'

                for spec in specs_rows:
                    key_el = spec.query_selector('th')
                    val_el = spec.query_selector('td')
                    if key_el and val_el:
                        key = normalize_key(key_el.inner_text().strip())
                        val = val_el.inner_text().strip()
                        if key != 'ASIN': # Ignore irrelevant keys
                            data[key] = val

            # --- FLIPKART Scraping Logic ---
            elif 'flipkart' in url:
                data['Source'] = 'Flipkart'
                title = page.query_selector('span.B_NuCI')
                price = page.query_selector('div._30jeq3._16Jk6d')
                
                # Flipkart often uses multiple specification sections
                specs_sections = page.query_selector_all('div._1UhVsV > div')
                
                # Product Description 
                # Flipkart often relies on specific content blocks for descriptions
                description_el = page.query_selector('div._1mXfK-')
                data['Description'] = description_el.inner_text().strip()[:200] + "..." if description_el else 'No description found'
                
                data['Product'] = title.inner_text().strip() if title else 'N/A'
                data['Price'] = price.inner_text().strip() if price else 'N/A'

                for section in specs_sections:
                    rows = section.query_selector_all('tr')
                    for row in rows:
                        cells = row.query_selector_all('td')
                        if len(cells) == 2:
                            key = normalize_key(cells[0].inner_text().strip())
                            val = cells[1].inner_text().strip()
                            data[key] = val
            
            # --- General/Fallback Logic ---
            else:
                data['Source'] = 'General Scrape'
                # Fallback for sites not explicitly targeted
                title_el = page.query_selector('h1') or page.query_selector('title')
                desc_el = page.query_selector('meta[name="description"]')

                data['Product'] = title_el.inner_text().strip() if title_el else page.title()
                
                description_content = desc_el.get_attribute('content') if desc_el else 'No description found'
                data['Description'] = (description_content[:200] + "...") if description_content and isinstance(description_content, str) else 'No description found'

                # Try to find a prominent price indicator (best effort)
                price_el = page.query_selector('.price') or page.query_selector('[class*="price"]')
                data['Price'] = price_el.inner_text().strip() if price_el else 'N/A'

            browser.close()
            
            if not data or len(data) <= 2: # If only title and source are found
                 # Try to find list features as a fallback
                for i, ul in enumerate(page.query_selector_all('ul, ol')[:3]):
                    items = [li.inner_text().strip() for li in ul.query_selector_all('li')[:5]]
                    if items and len(items) > 1:
                        data[f'Feature List {i+1}'] = ', '.join(items)


            logger.info(f"Scraped {len(data)} features from {url}")
            return data

    except Exception as e:
        logger.error(f"Scraping error for {url}: {e}")
        # The specific error for Playwright not being installed might show up here,
        # but in a typical environment, this is ready to go.
        return {'error': f'Failed to scrape {url}. Ensure the URL is correct and the site structure hasn\'t changed. Error: {str(e)}'}


@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON payload'}), 400

    url1, url2 = data.get('url1'), data.get('url2')
    if not (url1 and url2):
        return jsonify({'error': 'Both URLs are required'}), 400
    if not (is_valid_url(url1) and is_valid_url(url2)):
        return jsonify({'error': 'URLs must start with http:// or https://'}), 400

    logger.info(f"Comparing: {url1} vs {url2}")
    
    # Run scraping synchronously (Flask is thread-per-request, so this is fine)
    result1 = scrape_features(url1)
    result2 = scrape_features(url2)

    if 'error' in result1:
        return jsonify({'error': result1['error']}), 400
    if 'error' in result2:
        return jsonify({'error': result2['error']}), 400

    return jsonify({'data1': result1, 'data2': result2})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'Universal Feature Comparator API',
        'version': '2.0.0 (Playwright)',
        'endpoints': {
            '/compare': 'POST - Compare features from two URLs',
            '/health': 'GET - Health check'
        }
    })

@app.route('/meta')
def meta():
    return jsonify({
        "endpoints": {
            "compare": "POST - Compare features from two URLs",
            "health": "GET - Health check"
        },
        "name": "Universal Feature Comparator API",
        "version": "2.0.0 (Playwright)"
    })



