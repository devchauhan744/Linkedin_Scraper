from scraper import fetch_jobs
from storage import save_to_excel, save_to_sql_server
from datetime import datetime
from config import KEYWORDS, LOCATION, PAGES
import logging, random, time

def run_scraper():
    all_jobs, seen = [], set()
    logging.info("🚀 Starting LinkedIn Scraper...")

    for kw in KEYWORDS:
        for loc in LOCATION:
            logging.info(f"🔎 Searching for '{kw}' in '{loc}'")
            jobs = fetch_jobs(kw, loc, PAGES)
            for job in jobs:
                key = tuple(map(str.lower, (job[0], job[1], job[2], job[4])))
                if key not in seen:
                    seen.add(key)
                    all_jobs.append(job)
            time.sleep(random.uniform(3, 7))

    if all_jobs:
        filename = f"linkedin_jobs_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        save_to_excel(all_jobs, filename)
        save_to_sql_server(all_jobs)
        logging.info(f"✅ Saved {len(all_jobs)} unique job records.")
    else:
        logging.warning("⚠️ No job data found.")

if __name__ == "__main__":
    run_scraper()
