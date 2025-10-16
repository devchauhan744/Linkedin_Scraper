import requests
from bs4 import BeautifulSoup
import time, random, re, logging
from fake_useragent import UserAgent
from config import KEYWORDS, LOCATION, PAGES, HEADERS
from datetime import datetime  

ua = UserAgent()
session = requests.Session()
session.headers.update(HEADERS)

# -------------------------------
#  About the job extractor (NEW)
# -------------------------------
def extract_about_job(url):
    """
    Extracts the 'About the job' section from a LinkedIn job page.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            logging.warning(f"⚠️ Failed to fetch page {url} (status: {resp.status_code})")
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")

        # Try to locate "About the job" header
        header = soup.find(lambda tag: tag.name and "About the job" in tag.get_text())
        about_text = ""

        if header:
            parts = []
            for s in header.find_next_siblings():
                if s.name and s.name.startswith("h"):
                    break
                parts.append(s.get_text(" ", strip=True))
            about_text = "\n\n".join(p for p in parts if p.strip())

        # Fallback
        if not about_text:
            desc = soup.find("div", class_=lambda c: c and "description" in c)
            if desc:
                about_text = desc.get_text(" ", strip=True)

        return about_text.strip()
    except Exception as e:
        logging.error(f"❌ Exception during About-job extraction for {url}: {e}")
        return ""

# -------------------------------
#  Contact info extraction
# -------------------------------
def extract_contact_info_from_html(html):
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    hr_emails = [e for e in emails if re.search(r"(hr|jobs|careers|recruit)", e, re.I)]
    email_result = ", ".join(set(hr_emails)) if hr_emails else (", ".join(set(emails)) if emails else "N/A")
    return email_result

# -------------------------------
#  Job Description (backup)
# -------------------------------
def extract_job_description(html):
    soup = BeautifulSoup(html, "html.parser")
    desc_tag = soup.find("div", class_="show-more-less-html__content")
    if desc_tag:
        return desc_tag.get_text('\n', strip=True)
    else:
        return "N/A"
    
# Company Website and Company Linkedin Url
def extract_company_info(link):
    """
    Extracts company LinkedIn URL and company website from the job page.
    """
    try:
        resp = requests.get(link, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return "N/A", "N/A"

        soup = BeautifulSoup(resp.text, "html.parser")

        # --- LinkedIn Company URL ---
        company_linkedin_url = "N/A"
        company_anchor = soup.find("a", href=True, string=re.compile(r"View company page", re.I))
        if company_anchor:
            company_linkedin_url = "https://www.linkedin.com" + company_anchor["href"]

        # --- Company Website ---
        company_website = "N/A"
        for a in soup.find_all("a", href=True):
            if re.search(r"(www\.|http).*", a["href"]) and not a["href"].startswith("/"):
                if any(word in a.text.lower() for word in ["website", "company site", "visit site"]):
                    company_website = a["href"]
                    break

        return company_linkedin_url, company_website

    except Exception as e:
        logging.error(f"❌ Error extracting company info for {link}: {e}")
        return "N/A", "N/A"

# -------------------------------
#  Job type / contract / industry
# -------------------------------
def detect_job_type(title, description):
    text = (title + " " + description).lower()
    job_types = {
        "Software Engineer": ["software engineer", "developer", "programmer", "backend", "frontend", "full stack", "python", "java", "c++"],
        "Data Analyst": ["data analyst", "data scientist", "machine learning", "ml", "ai", "analytics", "data"],
        "Marketing": ["marketing", "seo", "content", "social media", "brand"],
        "Sales": ["sales", "business development", "bd", "account manager"],
        "HR": ["hr", "human resources", "recruiter", "talent"],
        "Finance": ["finance", "accounting", "financial", "cpa", "audit"],
        "Customer Support": ["customer support", "cs", "client services", "help desk"],
    }
    for job_type, keywords in job_types.items():
        for kw in keywords:
            if kw in text:
                return job_type
    return "Other"

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
    else:
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
        for kw in keywords:
            if kw in text:
                return industry
    return "Other"

# -------------------------------
#  Main job fetching
# -------------------------------
def fetch_jobs(keyword, location, pages):
    jobs = []

    for page in range(pages):
        start = page * 25
        if start >= 975:
            print("✅ Reached LinkedIn's 1000-job limit. Stopping.")
            break

        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location={location}&f_WT=2&f_TPR=r86400&start={start}"
        headers = session.headers.copy()
        headers["User-Agent"] = ua.random

        try:
            resp = session.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching page {page+1}: {e}")
            time.sleep(random.uniform(10, 20))
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
                hiring_person_url = "N/A"

                # --- NEW: About the job text ---
                about_job = ""
                if link != "N/A" and link.startswith("http"):
                    about_job = extract_about_job(link)

                # --- Fallback to normal extraction if needed ---
                if not about_job:
                    job_page = session.get(link, headers=headers, timeout=20)
                    if job_page.status_code == 200:
                        description = extract_job_description(job_page.text)
                    else:
                        description = "N/A"
                else:
                    description = about_job

                # --- Classification ---
                crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                job_type = detect_job_type(title, description)
                contract_type = detect_contract_type(title, description)
                industry = detect_industry(title, description, company)

                jobs.append([
                    title, company, city, state, country, post_time, link,
                    email, description, company_website, company_url, crawl_time,
                    job_type, contract_type, industry, hiring_person_url
                ])

            except Exception as e:
                print(f"⚠️ Skipping a card due to error: {e}")
                continue

        delay = random.uniform(5, 12)
        print(f"⏳ Waiting {delay:.2f} seconds before next page...")
        time.sleep(delay)

    return jobs
