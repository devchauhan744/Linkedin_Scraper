# import requests
# from bs4 import BeautifulSoup

# # LinkedIn company page (UK)
# url = "https://www.linkedin.com/company/shatterproof"

# # LinkedIn often blocks direct requests, so set headers to mimic a browser
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
# }

# response = requests.get(url, headers=headers)

# if response.status_code != 200:
#     print(f"Failed to fetch page: {response.status_code}")
#     exit()

# soup = BeautifulSoup(response.text, "html.parser")

# # Employee size info is often in <dd> tags with specific class, or in About section
# # This may change, so inspect the page if needed
# employee_size_text = None
# for dd in soup.find_all("dd"):
#     if "employees" in dd.get_text().lower():
#         employee_size_text = dd.get_text(strip=True)
#         break

# if employee_size_text:
#     print(f"Employee size: {employee_size_text}")
# else:
#     print("Employee size info not found on the page")

import requests
from bs4 import BeautifulSoup

# List of LinkedIn company URLs
company_urls = [
    "https://www.linkedin.com/company/uniscent-parf%C3%BCm",
    "https://www.linkedin.com/company/carrot-fertility",
    "https://www.linkedin.com/company/us-bank",
    "https://www.linkedin.com/company/est%C3%BAdio-ceno",
    "https://www.linkedin.com/company/eblajewels",
    "https://www.linkedin.com/company/honeywell",
    "https://www.linkedin.com/company/the-mcclatchy-company",
    "https://www.linkedin.com/company/atlassian",
    "https://www.linkedin.com/company/riverside-fm"
]

# Mimic browser headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
}

results = []

for url in company_urls:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        results.append({"url": url, "employee_size": "Failed to fetch"})
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    employee_size_text = None
    for dd in soup.find_all("dd"):
        if "employees" in dd.get_text().lower():
            employee_size_text = dd.get_text(strip=True)
            break

    if not employee_size_text:
        employee_size_text = "Not found / may require login"

    results.append({"url": url, "employee_size": employee_size_text})

# Print results
for r in results:
    print(f"{r['url']} => {r['employee_size']}")
