import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url: str) -> str:
    """
    Fetches the HTML of a webpage, removes scripts/styles, and returns clean text.
    Returns an empty string if the site is unreachable.
    """
    if not url:
        return ""
        
    try:
        if not url.startswith('http'):
            url = 'https://' + url
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Timeout quickly to avoid hanging on dead sites
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return ""
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove noisy elements
        for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Truncate to avoid context window explosion (5000 chars is usually enough for a homepage)
        return text[:5000]
    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        return ""
