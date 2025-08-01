import cx_Oracle
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("db_username")
password = os.getenv("db_password")

conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)

def fetch_inventory_alerts():
    cursor = conn.cursor()
    out_cursor = cursor.var(cx_Oracle.CURSOR)
    
    cursor.callfunc("GetInventoryAlerts", out_cursor)
    results = out_cursor.getvalue()
    
    columns = [col[0] for col in results.description]
    rows = results.fetchall()
    df = pd.DataFrame(rows, columns=columns)
    return df