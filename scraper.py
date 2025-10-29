#this is my scraper.py
# scraper.py
import requests
from bs4 import BeautifulSoup
import time, random, re, logging
from fake_useragent import UserAgent
from config import KEYWORDS, LOCATION, PAGES, HEADERS
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

# -------------------------
# SETUP
# -------------------------
ua = UserAgent()
session = requests.Session()
session.headers.update(HEADERS)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Cache company size results to avoid duplicate requests
company_cache = {}

# -------------------------
# CONTACT INFO
# -------------------------
def extract_contact_info_from_html(html):
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    hr_emails = [e for e in emails if re.search(r"(hr|jobs|careers|recruit)", e, re.I)]
    return ", ".join(set(hr_emails)) if hr_emails else (", ".join(set(emails)) if emails else "N/A")
# -------------------------
# EMPLOYEE SIZE SCRAPER
# -------------------------
def normalize_linkedin_url(url):
    """Force LinkedIn company URLs to use www.linkedin.com format."""
    from urllib.parse import urlparse, urlunparse
    if not url:
        return None
    parsed = urlparse(url)
    # Force domain to www.linkedin.com
    netloc = "www.linkedin.com"
    # Keep only the path (e.g., /company/foo)
    path = parsed.path.rstrip("/")
    if not path.startswith("/company/"):
        return None
    return urlunparse(("https", netloc, path, "", "", ""))

def get_employee_size(url, retries=3):
    """Fetch employee size from LinkedIn company page with retries and caching."""
    url = normalize_linkedin_url(url)
    if not url:
        return "Invalid URL"

    # ✅ Return from cache if we already fetched it
    if url in company_cache:
        return company_cache[url]

    for attempt in range(1, retries + 1):
        try:
            headers = {'User-Agent': ua.random}
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                logging.warning(f"⚠️ [{response.status_code}] Failed to fetch {url} (attempt {attempt})")
                time.sleep(random.uniform(3, 6))
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            size_text = None
            for dd in soup.find_all("dd"):
                if "employees" in dd.get_text().lower():
                    size_text = dd.get_text(strip=True)
                    break

            # ✅ Cache the result even if it's "Not found"
            company_cache[url] = size_text if size_text else "Not found / may require login"
            return company_cache[url]

        except Exception as e:
            logging.warning(f"⚠️ Error fetching size for {url} (attempt {attempt}): {e}")
            time.sleep(random.uniform(3, 6))

    company_cache[url] = "Failed to fetch"
    return "Failed to fetch"

# -------------------------
# JOB DESCRIPTION
# -------------------------
def extract_job_description(url_or_html, is_url=True):
    if is_url:
        headers = {'User-Agent': ua.random}
        try:
            response = requests.get(url_or_html, headers=headers, timeout=15)
            response.raise_for_status()
            html = response.text
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching URL: {e}")
            return "N/A"
    else:
        html = url_or_html

    soup = BeautifulSoup(html, "html.parser")
    desc_tag = soup.find("div", class_="description__text") or soup.find("div", class_="show-more-less-html__content")
    return desc_tag.get_text("\n", strip=True) if desc_tag else "N/A"

# -------------------------
# CLEAN LINKEDIN REDIRECT
# -------------------------
def clean_linkedin_redirect(url):
    if not url.startswith("http"):
        return url
    parsed = urlparse(url)
    if "linkedin.com/redir/redirect" in parsed.netloc + parsed.path:
        query = parse_qs(parsed.query)
        real_url = unquote(query.get("url", [""])[0])
        return real_url if real_url else url
    return url

# # -------------------------
# # JOB TYPE, CONTRACT, INDUSTRY
# # -------------------------
# def detect_job_type(title, description):
#     text = (title + " " + description).lower()
#     job_types = {
#         "Software Engineer": ["software engineer", "developer", "programmer", "backend", "frontend", "full stack", "python", "java", "c++"],
#         "Data Analyst": ["data analyst", "data scientist", "machine learning", "ml", "ai", "analytics", "data"],
#         "Marketing": ["marketing", "seo", "content", "social media", "brand"],
#         "Sales": ["sales", "business development", "bd", "account manager"],
#         "HR": ["hr", "human resources", "recruiter", "talent"],
#         "Finance": ["finance", "accounting", "financial", "cpa", "audit"],
#         "Customer Support": ["customer support", "cs", "client services", "help desk"],
#     }
#     for job_type, keywords in job_types.items():
#         if any(kw in text for kw in keywords):
#             return job_type
#     return "Other"

def detect_contract_type(title, description):
    text = (title + " " + description).lower()
    if any(word in text for word in ["full-time", "full time", "permanent role"]):
        return "Full-time"
    elif any(word in text for word in ["part-time", "part time"]):
        return "Part-time"
    elif any(word in text for word in ["intern", "internship", "trainee"]):
        return "Internship"
    elif any(word in text for word in ["contract", "freelance", "temporary", "consultant"]):
        return "Contract/Freelancer"
    elif any(word in text for word in ["remote", "work from home", "wfh"]):
        return "Remote"
    return "Other"

def detect_industry(title, description, company=""):
    text = (title + " " + description + " " + company).lower()
    industries = {
        "Information Technology": ["software", "developer", "engineer", "it", "saas", "tech", "cloud", "data", "machine learning", "ai", "cybersecurity", "network", "devops"],
        "Finance": ["finance", "financial", "bank", "insurance", "accounting", "audit", "cpa", "investment", "wealth", "tax", "actuary"],
        "Healthcare": ["medical", "healthcare", "hospital", "clinic", "nurse", "pharma", "biotech", "dental", "veterinary", "surgical", "doctor"],
        "Construction": ["construction", "civil", "architect", "structural", "building", "contractor", "mechanical", "plumbing", "electrical", "hvac"],
        "Education": ["school", "university", "college", "teacher", "professor", "tutor", "education", "training", "academic"],
        "Manufacturing": ["manufacturing", "production", "factory", "plant", "assembly", "machinery"],
        "Retail": ["retail", "store", "sales associate", "shop", "customer service"],
        "Marketing & Advertising": ["marketing", "seo", "branding", "advertising", "social media", "digital marketing", "content"],
        "Real Estate": ["real estate", "property", "broker", "estate", "mortgage", "leasing"],
        "Legal": ["law", "legal", "attorney", "paralegal", "litigation"],
        "Transportation & Logistics": ["logistics", "transportation", "supply chain", "warehouse", "driver", "shipping"],
    }
    for industry, keywords in industries.items():
        if any(kw in text for kw in keywords):
            return industry
    return "Other"

# -------------------------
# MAIN JOB FETCHER
# -------------------------
def fetch_jobs(keyword, location, pages):
    jobs = []
    for page in range(pages):
        start = page * 25
        if start >= 975:
            print("✅ Reached LinkedIn's 1000-job limit. Stopping.")
            break

        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={keyword}&location={location}&f_WT=2&f_TPR=r86400&start={start}"
        )
        headers = session.headers.copy()
        headers["User-Agent"] = ua.random

        try:
            resp = session.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching page {page+1}: {e}")
            time.sleep(random.uniform(5,12))
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("li")
        if not cards:
            print("⚠️ No more job cards found, stopping...")
            break

        for card in cards:
            try:
                title = card.find("h3").get_text(strip=True) if card.find("h3") else "N/A"
                company = card.find("h4").get_text(strip=True) if card.find("h4") else "N/A"
                location_full = card.find("span", class_="job-search-card__location").get_text(strip=True) if card.find("span", class_="job-search-card__location") else "N/A"
                parts = [x.strip() for x in location_full.split(",")]
                city = parts[0] if len(parts) > 0 else "N/A"
                state = parts[1] if len(parts) > 1 else "N/A"
                country = parts[2] if len(parts) > 2 else "N/A"
                link_tag = card.find("a")
                link = link_tag["href"].split("?")[0] if link_tag and link_tag.get("href") else "N/A"
                post_time = card.find("time")["datetime"] if card.find("time") else "N/A"
                email, description, company_website, company_url = "N/A", "N/A", "N/A", "N/A"

                # Find company URL from card
                for a in card.find_all("a", href=True):
                    href = a["href"]
                    if "/company/" in href or "companyId" in href:
                        company_url = href.split("?")[0]
                        break

                # Fetch job description
                if link != "N/A" and link.startswith("http"):
                    try:
                        description = extract_job_description(link, is_url=True)
                        email = extract_contact_info_from_html(requests.get(link, headers=headers).text)
                    except:
                        description = "N/A"

                # Fetch company website (optional)
                if company_url != "N/A":
                    try:
                        comp_page = session.get(company_url, headers=headers, timeout=20)
                        if comp_page.status_code == 200:
                            c_email = extract_contact_info_from_html(comp_page.text)
                            if c_email != "N/A":
                                email = c_email
                            soup_comp = BeautifulSoup(comp_page.text, "html.parser")
                            website_tag = (
                                soup_comp.find("dt", string=re.compile("Website", re.I)) or
                                soup_comp.find("p", string=re.compile("Website", re.I)) or
                                soup_comp.find("a", href=True, text=re.compile(r"website|site|home", re.I))
                            )
                            if website_tag:
                                dd = website_tag.find_next_sibling("dd") if website_tag.name == "dt" else None
                                if dd and dd.find("a", href=True):
                                    company_website = dd.find("a", href=True)["href"]
                                elif website_tag.name == "p":
                                    p_next = website_tag.find_next_sibling("p")
                                    if p_next and p_next.find("a", href=True):
                                        company_website = p_next.find("a", href=True)["href"]
                                elif website_tag.name == "a":
                                    company_website = website_tag["href"]

                                if company_website.startswith("http"):
                                    company_website = clean_linkedin_redirect(company_website)
                    except:
                        pass
                if company_url != "N/A":
                    employee_size = get_employee_size(company_url)
                    time.sleep(random.uniform(5, 10))
                    
                crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # job_type = detect_job_type(title, description)
                contract_type = detect_contract_type(title, description)
                industry = detect_industry(title, description, company)

                jobs.append([
                    title, company, city, state, country, post_time, link,
                    email, description, company_website, company_url, crawl_time,
                    # job_type
                    contract_type, industry,employee_size
                ])

            except Exception as e:
                print(f"⚠️ Skipping a card due to error: {e}")
                continue

        delay = random.uniform(5,12)
        print(f"⏳ Waiting {delay:.2f} seconds before next page...")
        time.sleep(delay)

    return jobs
