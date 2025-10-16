#this is my run.py
from scraper import fetch_jobs
from storage import save_to_excel
from datetime import datetime
import logging
from config import KEYWORDS, LOCATION, PAGES
import time, random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scraper():
    all_jobs = []

    try:
        print("🚀 Starting LinkedIn Job Scraper...")

        for keyword in KEYWORDS:
            for location in LOCATION:
                print(f"\n🔎 Scraping jobs for '{keyword}' in '{location}'...")
                jobs = fetch_jobs(keyword, location, PAGES)
                all_jobs.extend(jobs)
                time.sleep(random.uniform(5,15))

        if all_jobs:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.xlsx"
            save_to_excel(all_jobs, filename)
            print(f"✅ Saved {len(all_jobs)} job records to {filename}")
        else:
            print("⚠️ No job data found.")

    except Exception as e:
        logging.error(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    run_scraper()
