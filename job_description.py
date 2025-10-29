import requests
from bs4 import BeautifulSoup

# Target job page (or job detail URL)
url = "https://www.linkedin.com/jobs/view/4332880083/?alternateChannel=search&eBP=NOT_ELIGIBLE_FOR_CHARGING&trk=d_flagship3_search_srp_jobs&refId=pwT1dh34%2BtfxMhbCPH36gw%3D%3D&trackingId=S%2BxGjh3mVAjt62JW8fwWSg%3D%3D"

# -- 1. Set up headers and cookies --
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# You must manually copy your LinkedIn 'li_at' cookie value from your browser.
cookies = {
    "li_at": "PASTE_YOUR_LINKEDIN_LI_AT_COOKIE_HERE"
}

# -- 2. Make the request --
response = requests.get(url, headers=headers, cookies=cookies)

if response.status_code != 200:
    print(f"Request failed: {response.status_code}")
    print(response.text[:500])
    exit()

# -- 3. Parse HTML --
soup = BeautifulSoup(response.text, "html.parser")

# -- 4. Locate the "About the job" div --
about_div = soup.select_one("div.jobs-box__html-content.jobs-description-content__text--stretch")

if about_div:
    about_text = about_div.get_text(separator="\n").strip()
    print("\n✅ About the job:\n")
    print(about_text[:1500])  # print first 1500 characters
else:
    print("❌ Couldn't find job description (page likely needs JS or wrong cookie/session).")
