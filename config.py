#this is my config.py
# LinkedIn Scraper Configuration

LI_AT = "AQEDAVHDI2ED4PitAAABmiTZnkUAAAGaSOYiRU0AN3yvC-PIwN28cyUY5uViMkc63qO0ULs0HeJ7_n8VgsZXB8hZjCN6P4bJzhDDySYMfvWqngUQTNVo6grfsO2Zz4-ACIkVCHTYjRVyHnjd7-xsBc-M"
KEYWORDS = [".NET Developer","UI/UX","ASP.NET MVC","Front-End Developer","ASP.NET"]  # can be a list of keywords
LOCATION = ["Canada","Europe","Uk","Us","Australia"]            # can be a list of locations
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