# storage.py
import pandas as pd
import logging
from openpyxl.utils import get_column_letter
from sqlalchemy import text
from db_config import get_engine


def save_to_excel(data, filename="linkedin_jobs.xlsx"):
    try:
        df = create_dataframe(data)

        # ✅ Drop logical duplicates before saving
        # df.drop_duplicates(subset=["JobTitle", "Company", "City", "Country"], inplace=True)

        df.insert(0, "Sr No", range(1, len(df) + 1))

        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Jobs")
            adjust_excel_column_width(writer, df, "Jobs")

        logging.info(f"📁 Saved {len(df)} unique job records to {filename}")

    except Exception as e:
        logging.error(f"❌ Failed to save data to Excel: {e}")


def save_to_sql_server(data):
    """Save scraped job data into SQL Server (deduped)."""
    try:
        df = create_dataframe(data)
        # df.drop_duplicates(subset=["JobTitle", "Company", "City", "Country"], inplace=True)
        engine = get_engine()

        # ✅ Ensure unique index exists
        with engine.begin() as conn:
            conn.execute(text("""
                IF NOT EXISTS (
                    SELECT * FROM sys.indexes WHERE name = 'UQ_JobTitle_Company_City_Country'
                )
                CREATE UNIQUE INDEX UQ_JobTitle_Company_City_Country
                ON LinkedInJobs (JobTitle, Company, City, Country);
            """))

        # # ✅ Insert data safely (ignore duplicates)
        # try:
        #     df.to_sql("LinkedInJobs", con=engine, if_exists="append", index=False)
        #     logging.info("💾 Data successfully saved to SQL Server (duplicates ignored).")
        # except Exception as insert_error:
        #     logging.warning(f"⚠️ Duplicate rows skipped during SQL insert: {insert_error}")

    except Exception as e:
        logging.error(f"❌ Failed to save data to SQL Server: {e}")


def create_dataframe(data):
    return pd.DataFrame(
        data,
        columns=[
            "JobTitle", "Company", "City", "State", "Country", "DatePosted",
            "JobLink", "Email", "JobDescription", "CompanyWebsite",
            "CompanyLinkedInURL", "CrawlTime", "ContractType", "Industry", "EmployeeSize"
        ]
    )


def adjust_excel_column_width(writer, df, sheet_name):
    worksheet = writer.sheets[sheet_name]
    for i, col in enumerate(df.columns, 1):
        max_length = max(df[col].astype(str).map(len).max(), len(col))
        worksheet.column_dimensions[get_column_letter(i)].width = max_length + 5
