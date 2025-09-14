# Universal Feature Comparator

A web application that compares features of any two products or items by scraping their web pages and displaying results in a side-by-side comparison table.

## Project Structure

```
universal-feature-comparator/
├── index.html          # Main HTML structure
├── styles.css          # CSS styling
├── script.js           # Frontend JavaScript
├── app.py              # Python Flask backend
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Features

- **Universal Comparison**: Compare any two products or items from web URLs
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Scraping**: Extracts features dynamically from web pages
- **Error Handling**: Graceful error handling with user-friendly messages
- **Clean UI**: Modern, professional interface using Tailwind CSS

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Node.js (optional, for serving static files)

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask Server**
   ```bash
   python app.py
   ```
   
   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Serve Static Files**
   
   Option A: Using Python's built-in server
   ```bash
   python -m http.server 8000
   ```
   
   Option B: Using Node.js http-server
   ```bash
   npm install -g http-server
   http-server
   ```
   
   Option C: Simply open `index.html` in your browser (may have CORS issues)

2. **Access the Application**
   
   Open your browser and go to `http://localhost:8000` (or the port you're using)

## Usage

1. Enter two URLs of products or items you want to compare
2. Click "Compare Features"
3. Wait for the scraping process to complete
4. View the side-by-side comparison table

## Customization

### Backend Customization

The `scrape_features()` function in `app.py` can be customized for specific websites:

```python
def scrape_features(url):
    # Add your custom scraping logic here
    # For example, for Amazon products:
    title = soup.find('span',
