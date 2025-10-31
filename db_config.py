from sqlalchemy import create_engine

DB_SERVER = "R2D\\SQLEXPRESS"
DB_NAME = "LinkedInJobsDB"

CONNECTION_STRING = f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"

def get_engine():
    return create_engine(CONNECTION_STRING, fast_executemany=True)
