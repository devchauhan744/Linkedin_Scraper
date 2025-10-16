#this is my storage.py
import pandas as pd
from openpyxl.utils import get_column_letter
import logging

def save_to_excel(data, filename="linkedin_jobs.xlsx"):
    try:
        df = pd.DataFrame(
            data,
            columns=[
                "Job Title", "Company", "City", "State", "Country", "Date",
                "Job Link", "Email", "Job Description", "Company Website",
                "Company LinkedIn URL", "Crawl Time", "Contract Type", "Industry", "Employee Size"
            ])

        df.insert(0, "Sr No", range(1, len(df) + 1))
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Jobs")
            adjust_excel_column_width(writer, df, "Jobs")
        logging.info(f"📁 Saved job data to {filename}")
    except Exception as e:
        logging.error(f"❌ Failed to save data to Excel: {e}")

def adjust_excel_column_width(writer, df, sheet_name):
    worksheet = writer.sheets[sheet_name]
    for i, col in enumerate(df.columns, 1):
        max_length = max(df[col].astype(str).map(len).max(), len(col))
        worksheet.column_dimensions[get_column_letter(i)].width = max_length + 5
