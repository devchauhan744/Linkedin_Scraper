import requests
from config import LI_AT

url = "https://www.linkedin.com/feed/"
cookies = {"li_at": LI_AT}
headers = {"User-Agent": "Mozilla/5.0"}

r = requests.get(url, cookies=cookies, headers=headers)
print("Status Code:", r.status_code)
print("Redirected to:", r.url)
if "feed" in r.text.lower():
    print("✅ Cookie works, logged in!")
else:
    print("❌ Cookie invalid!")
