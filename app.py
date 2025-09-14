# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# from bs4 import BeautifulSoup
# import logging

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def scrape_features(url):
#     """
#     Scrape features from a given URL.
#     This function needs to be customized based on the specific websites you're scraping.
#     """
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
    
#     try:
#         logger.info(f"Scraping URL: {url}")
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()  # Raise an error for bad status codes
        
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # *** CUSTOMIZE THIS SECTION FOR YOUR SPECIFIC USE CASE ***
#         features = {}
        
#         # Try to extract common product information
#         title_tag = soup.find('h1')
#         if title_tag:
#             features['Product'] = title_tag.get_text(strip=True)
        
#         # Try to extract price (common selectors)
#         price_selectors = ['.price', '.cost', '[class*="price"]', '[id*="price"]']
#         for selector in price_selectors:
#             price_element = soup.select_one(selector)
#             if price_element:
#                 features['Price'] = price_element.get_text(strip=True)
#                 break
        
#         # Try to extract description or key features
#         desc_selectors = ['.description', '.product-description', '[class*="description"]']
#         for selector in desc_selectors:
#             desc_element = soup.select_one(selector)
#             if desc_element:
#                 features['Description'] = desc_element.get_text(strip=True)[:200] + "..."
#                 break
        
#         # Extract meta information
#         meta_description = soup.find('meta', attrs={'name': 'description'})
#         if meta_description and 'Description' not in features:
#             features['Description'] = meta_description.get('content', '')[:200] + "..."
        
#         # Fallback for description
#         if 'Description' not in features:
#             features['Description'] = "No description found"
        
#         # If no specific features found, extract some general information
#         if len(features) <= 1:  # Only title found or nothing found
#             feature_lists = soup.find_all(['ul', 'ol'])
#             if feature_lists:
#                 for i, ul in enumerate(feature_lists[:3]):  # Limit to first 3 lists
#                     items = ul.find_all('li')
#                     if items:
#                         features[f'Feature List {i+1}'] = ', '.join([li.get_text(strip=True) for li in items[:5]])
        
#         # Fallback: if still no features, return basic page info
#         if not features:
#             title_tag = soup.find('title')
#             features = {
#                 'Title': title_tag.get_text(strip=True) if title_tag else 'No title found',
#                 'URL': url,
#                 'Content Length': f"{len(response.content)} bytes"
#             }
        
#         logger.info(f"Successfully scraped {len(features)} features from {url}")
#         return features
        
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Request error for {url}: {str(e)}")
#         return {'error': f'Failed to fetch {url}: {str(e)}'}
#     except Exception as e:
#         logger.error(f"Parsing error for {url}: {str(e)}")
#         return {'error': f'An error occurred while scraping {url}: {str(e)}'}

# @app.route('/compare', methods=['POST'])
# def compare():
#     """
#     Main comparison endpoint that accepts two URLs and returns scraped features.
#     """
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'No JSON data provided.'}), 400
            
#         url1 = data.get('url1')
#         url2 = data.get('url2')
        
#         if not url1 or not url2:
#             return jsonify({'error': 'Both URLs are required.'}), 400
        
#         # Validate URLs
#         if not (url1.startswith('http://') or url1.startswith('https://')):
#             return jsonify({'error': 'URL 1 must start with http:// or https://'}), 400
#         if not (url2.startswith('http://') or url2.startswith('https://')):
#             return jsonify({'error': 'URL 2 must start with http:// or https://'}), 400
        
#         logger.info(f"Comparing URLs: {url1} vs {url2}")
        
#         # Scrape both URLs
#         data1 = scrape_features(url1)
#         data2 = scrape_features(url2)
        
#         # Check for errors
#         if 'error' in data1:
#             return jsonify({'error': data1['error']}), 400
#         if 'error' in data2:
#             return jsonify({'error': data2['error']}), 400
        
#         logger.info("Comparison completed successfully")
#         return jsonify({'data1': data1, 'data2': data2})
        
#     except Exception as e:
#         logger.error(f"Unexpected error in compare endpoint: {str(e)}")
#         return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Simple health check endpoint."""
#     return jsonify({'status': 'healthy', 'message': 'Universal Feature Comparator API is running'})

# @app.route('/', methods=['GET'])
# def home():
#     """Basic home endpoint with API information."""
#     return jsonify({
#         'name': 'Universal Feature Comparator API',
#         'version': '1.0.0',
#         'endpoints': {
#             '/compare': 'POST - Compare features from two URLs',
#             '/health': 'GET - Health check'
#         }
#     })

# if __name__ == '__main__':
#     print("Starting Universal Feature Comparator API...")
#     print("API will be available at http://localhost:5000")
#     print("Use POST /compare with JSON: {'url1': 'url1', 'url2': 'url2'}")
#     app.run(debug=True, host='0.0.0.0', port=5000)



from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)
CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common selectors for scraping
PRICE_SELECTORS = ['.price', '.cost', '[class*="price"]', '[id*="price"]']
DESC_SELECTORS = ['.description', '.product-description', '[class*="description"]']

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    )
}

def is_valid_url(url):
    return url.startswith(('http://', 'https://'))

def extract_text(soup, selectors, label, truncate=200):
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)[:truncate] + "..."
    return None

def scrape_features(url):
    try:
        logger.info(f"Scraping: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        features = {}

        # Title
        title = soup.find('h1')
        if title:
            features['Product'] = title.get_text(strip=True)

        # Price
        price = extract_text(soup, PRICE_SELECTORS, 'Price')
        if price:
            features['Price'] = price

        # Description
        description = extract_text(soup, DESC_SELECTORS, 'Description')
        if not description:
            meta = soup.find('meta', attrs={'name': 'description'})
            content = meta.get('content', '') if meta else None
            if isinstance(content, str):
                description = content[:200] + "..."
            else:
                description = "No description found"
        features['Description'] = description

        # Feature lists
        if len(features) <= 1:
            import bs4
            for i, ul in enumerate(soup.find_all(['ul', 'ol'])[:3]):
                if isinstance(ul, bs4.element.Tag):
                    items = [li.get_text(strip=True) for li in ul.find_all('li')[:5]]
                    if items:
                        features[f'Feature List {i+1}'] = ', '.join(items)

        # Fallback
        if not features:
            page_title = soup.find('title')
            features = {
                'Title': page_title.get_text(strip=True) if page_title else 'No title found',
                'URL': url,
                'Content Length': f"{len(response.content)} bytes"
            }

        logger.info(f"Scraped {len(features)} features from {url}")
        return features

    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return {'error': f'Failed to fetch {url}: {str(e)}'}
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return {'error': f'Error scraping {url}: {str(e)}'}

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
    result1, result2 = scrape_features(url1), scrape_features(url2)

    if 'error' in result1:
        return jsonify({'error': result1['error']}), 400
    if 'error' in result2:
        return jsonify({'error': result2['error']}), 400

    return jsonify({'data1': result1, 'data2': result2})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'Universal Feature Comparator API',
        'version': '1.1.0',
        'endpoints': {
            '/compare': 'POST - Compare features from two URLs',
            '/health': 'GET - Health check'
        }
    })

if __name__ == '__main__':
    logger.info("Starting Universal Feature Comparator API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
