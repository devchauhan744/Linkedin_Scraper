# run.py
from scraper import fetch_jobs
from storage import save_to_excel, save_to_sql_server
from datetime import datetime
import logging, time, random
from config import KEYWORDS, LOCATION, PAGES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_scraper():
    all_jobs = []
    seen_jobs = set()  # ✅ For logical duplicate tracking

    try:
        print("🚀 Starting LinkedIn Job Scraper...")

        for keyword in KEYWORDS:
            for location in LOCATION:
                print(f"\n🔎 Scraping jobs for '{keyword}' in '{location}'...")
                jobs = fetch_jobs(keyword, location, PAGES)

                for job in jobs:
                    # Ensure job has at least 5 fields
                    if len(job) < 5:
                        continue

                    # Logical duplicate key
                    key = (
                        str(job[0]).strip().lower(),  # JobTitle
                        str(job[1]).strip().lower(),  # Company
                        str(job[2]).strip().lower(),  # City
                        str(job[4]).strip().lower()   # Country
                    )

                    if key not in seen_jobs:
                        seen_jobs.add(key)
                        all_jobs.append(job)
                    else:
                        logging.info(f"🟡 Skipped duplicate: {job[0]} - {job[1]} ({job[2]}, {job[4]})")

                time.sleep(random.uniform(5, 15))  # polite delay between requests

        if all_jobs:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.xlsx"
            save_to_excel(all_jobs, filename)
            save_to_sql_server(all_jobs)
            print(f"✅ Saved {len(all_jobs)} unique job records to {filename} and SQL Server.")
        else:
            print("⚠️ No job data found.")

    except Exception as e:
        logging.error(f"❌ An error occurred: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_scraper()
