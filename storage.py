import pandas as pd, logging
from sqlalchemy import text
from openpyxl.utils import get_column_letter
from db_config import get_engine

def create_dataframe(data):
    cols = [
        "JobTitle", "Company", "City", "State", "Country", "DatePosted",
        "JobLink", "Email", "JobDescription", "CompanyWebsite",
        "CompanyLinkedInURL", "CrawlTime", "ContractType", "Industry", "EmployeeSize"
    ]
    return pd.DataFrame(data, columns=cols)

def adjust_column_width(writer, df, sheet):
    ws = writer.sheets[sheet]
    for i, col in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = min(80, max(df[col].astype(str).map(len).max(), len(col)) + 5)

def save_to_excel(data, filename):
    df = create_dataframe(data)
    df.insert(0, "Sr No", range(1, len(df) + 1))
    with pd.ExcelWriter(filename, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Jobs")
        adjust_column_width(w, df, "Jobs")
    logging.info(f"💾 Saved {len(df)} jobs to {filename}")

def save_to_sql_server(data):
    try:
        df = create_dataframe(data)
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(text("""
                IF OBJECT_ID('dbo.LinkedInJobs', 'U') IS NULL
                CREATE TABLE LinkedInJobs (
                    JobTitle NVARCHAR(255), Company NVARCHAR(255),
                    City NVARCHAR(255), State NVARCHAR(255), Country NVARCHAR(255),
                    DatePosted NVARCHAR(50), JobLink NVARCHAR(MAX), Email NVARCHAR(MAX),
                    JobDescription NVARCHAR(MAX), CompanyWebsite NVARCHAR(MAX),
                    CompanyLinkedInURL NVARCHAR(MAX), CrawlTime DATETIME,
                    ContractType NVARCHAR(100), Industry NVARCHAR(100), EmployeeSize NVARCHAR(100)
                );
            """))
        df.to_sql("LinkedInJobs", con=engine, if_exists="append", index=False)
        logging.info("✅ Data saved to SQL Server.")
    except Exception as e:
        logging.error(f"❌ SQL Save failed: {e}")
