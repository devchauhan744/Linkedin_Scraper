import requests
from bs4 import BeautifulSoup

def fetch_job_description(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the job description section
    job_description_section = soup.find('div', {'class': 'description__text'})
    
    if job_description_section:
        return job_description_section.get_text(strip=True)
    else:
        return "Job description not found."

# URL of the LinkedIn job posting
url = 'https://ca.linkedin.com/jobs/view/data-analyst-at-helic-co-4314443439'

# Fetch and print the job description
job_description = fetch_job_description(url)
print(job_description)
