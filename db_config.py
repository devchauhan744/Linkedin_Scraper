# db_config.py
from sqlalchemy import create_engine

# Change these based on your setup
DB_SERVER = "DEVCHAUHAN\SQLEXPRESS01"       # or "YOUR_SERVER_NAME\\SQLEXPRESS"
DB_NAME = "LinkedInJobsDB"

# Example connection string for SQL Server using pyodbc
CONNECTION_STRING = (
    f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
)


def get_engine():
    return create_engine(CONNECTION_STRING)
