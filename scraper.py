import json
import requests, time, random, re, logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
from config import BASE_HEADERS, KEYWORDS, LOCATION, PAGES, REQUEST_TIMEOUT, RETRY_COUNT, DELAY_RANGE

# Setup
ua = UserAgent()
session = requests.Session()
session.headers.update(BASE_HEADERS)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

company_cache, job_cache = {}, {}

# ------------------------- Utility Helpers -------------------------
def safe_request(url, headers=None, retries=RETRY_COUNT, timeout=REQUEST_TIMEOUT):
    """Handle network errors with retry logic."""
    headers = headers or {"User-Agent": ua.random}
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.text
            logging.warning(f"⚠️ HTTP {r.status_code} for {url} (attempt {attempt})")
        except requests.RequestException as e:
            logging.warning(f"⚠️ Error fetching {url}: {e}")
        time.sleep(random.uniform(*DELAY_RANGE))
    return None

def extract_emails_from_html(html):
    """Extract HR/recruiter emails."""
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    hr_emails = [e for e in emails if re.search(r"(hr|career|recruit|jobs)", e, re.I)]
    return ", ".join(set(hr_emails)) if hr_emails else (", ".join(set(emails)) if emails else "N/A")

def clean_linkedin_redirect(url):
    """Extract real URL from LinkedIn redirect links."""
    parsed = urlparse(url)
    if "linkedin.com/redir/redirect" in parsed.netloc + parsed.path:
        real_url = unquote(parse_qs(parsed.query).get("url", [""])[0])
        return real_url or url
    return url

# ------------------------- Job Details Extractors -------------------------
def extract_job_description(view_url):
    """Fetch job description from LinkedIn guest job API (no login)."""
    if not view_url or view_url == "N/A":
        return "N/A"
    if view_url in job_cache:
        return job_cache[view_url]

    # Extract job ID from URL
    match = re.search(r"-(\d+)$", view_url)
    if not match:
        logging.warning(f"⚠️ Invalid job URL format: {view_url}")
        return "N/A"

    job_id = match.group(1)
    api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

    html = safe_request(api_url)
    if not html:
        job_cache[view_url] = "N/A"
        return "N/A"

    soup = BeautifulSoup(html, "html.parser")
    desc = soup.find("div", class_="show-more-less-html__markup")
    text = desc.get_text("\n", strip=True) if desc else "N/A"

    if text == "N/A" or len(text.strip()) < 40:
        logging.warning(f"⚠️ Empty description via API for {view_url}")
    else:
        logging.info(f"✅ Description fetched for job {job_id} ({len(text)} chars)")

    job_cache[view_url] = text
    return text

def get_employee_size(company_url):
    """Fetch company employee size with caching."""
    if not company_url:
        return "Invalid URL"
    if company_url in company_cache:
        return company_cache[company_url]

    html = safe_request(company_url)
    if not html:
        company_cache[company_url] = "Failed to fetch"
        return "Failed to fetch"

    soup = BeautifulSoup(html, "html.parser")
    size_text = next((dd.get_text(strip=True) for dd in soup.find_all("dd") if "employees" in dd.get_text().lower()), None)
    result = size_text or "Not found / may require login"
    company_cache[company_url] = result
    return result

# ------------------------- Classification -------------------------
def detect_contract_type(title, desc):
    text = (title + " " + desc).lower()
    if "full time" in text:
        return "Full-time"
    if "part time" in text:
        return "Part-time"
    if any(k in text for k in ["intern", "internship"]):
        return "Internship"
    if any(k in text for k in ["contract", "freelance"]):
        return "Contract"
    if any(k in text for k in ["remote", "wfh"]):
        return "Remote"
    return "Other"

def detect_industry(title, desc, company):
    text = (title + desc + company).lower()
    industries = {
        "IT": ["developer", "engineer", "software", "tech", "ai", "cloud"],
        "Finance": ["bank", "finance", "accounting"],
        "Healthcare": ["medical", "nurse", "clinic", "hospital"],
        "Education": ["school", "university", "teacher"],
        "Marketing": ["marketing", "seo", "brand"],
    }
    for k, v in industries.items():
        if any(i in text for i in v):
            return k
    return "Other"

# ------------------------- Main Scraper -------------------------
def fetch_jobs(keyword, location, pages=PAGES):
    jobs = []
    for page in range(pages):
        start = page * 25
        url = (
                 "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                 f"?keywords={keyword}"
                 f"&location={location}"
                 f"&f_TPR=r86400"   # posted in last 24 hours
                 f"&f_WT=2"         # remote jobs only
                 f"&start={start}"
)

        html = safe_request(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("li")
        if not cards:
            logging.info("⚠️ No more job cards found, stopping.")
            break

        for card in cards:
            try:
                title = card.find("h3").get_text(strip=True)
                company = card.find("h4").get_text(strip=True)
                loc = card.find("span", class_="job-search-card__location").get_text(strip=True)
                city, *rest = [x.strip() for x in loc.split(",")] + ["N/A"] * 2
                link_tag = card.find("a", href=True)
                job_link = link_tag["href"].split("?")[0] if link_tag else "N/A"
                post_time = card.find("time")["datetime"] if card.find("time") else "N/A"

                company_url = next((a["href"].split("?")[0] for a in card.find_all("a", href=True) if "/company/" in a["href"]), "N/A")

                description = extract_job_description(job_link)
                email = extract_emails_from_html(description)
                emp_size = get_employee_size(company_url) if company_url != "N/A" else "N/A"

                crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                contract_type = detect_contract_type(title, description)
                industry = detect_industry(title, description, company)

                jobs.append([
                    title, company, city, rest[0], rest[1], post_time, job_link,
                    email, description, "N/A", company_url, crawl_time,
                    contract_type, industry, emp_size
                ])
            except Exception as e:
                logging.warning(f"⚠️ Skipping job due to error: {e}")
                continue

        logging.info(f"⏳ Sleeping {DELAY_RANGE[1]}s before next page...")
        time.sleep(random.uniform(*DELAY_RANGE))
    return jobs
