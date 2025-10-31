# config.py
# LinkedIn Scraper Configuration

LI_AT = "AQEDAU0NCxMCXgIPAAABmjpbirkAAAGaXmgOuU0ABxQ7oETj7NUyfvKcaMITkqHlCXrjZQ06kxYe21QgyqwNiX4-c2J5z2blm0hcfjWc8PbR8nSXc2yJ4gcW48RZ61L9kcXkRVCpGChs6lHADK9FBVxm"

KEYWORDS = ["ASP.NET Developer", "C# Developer", "Backend Developer"]
LOCATION = ["Canada"]
PAGES = 2

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": f"li_at={LI_AT};",
    "Referer": "https://www.linkedin.com/",
    "Upgrade-Insecure-Requests": "1",
}

REQUEST_TIMEOUT = 15
RETRY_COUNT = 3
DELAY_RANGE = (4, 8)  # seconds between requests
