#this is my config.py
# LinkedIn Scraper Configuration

LI_AT = "AQEDAVHDI2EECMvfAAABmd0V4x4AAAGaASJnHk0AOPa99mD3uOYzPBf0Q1qqcKni_HPg1c0XBX52xOleW_QbKLVScihavoLCDMSdnhWeOA89r4xl92oenVhJFyLGcvuXG_ebG8KqECukN1Vi0rfTPKCe"
KEYWORDS = ["We are hiring","I am looking for"]  # can be a list of keywords
LOCATION = ["Europe","United States","United Kingdom","Australia","Canada"]            # can be a list of locations
PAGES = 20

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": f"li_at={LI_AT};",
    "Referer": "https://www.linkedin.com/",
    "Upgrade-Insecure-Requests": "1"
}