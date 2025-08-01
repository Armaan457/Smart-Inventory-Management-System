import cx_Oracle
import os
from dotenv import load_dotenv
load_dotenv()

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("db_username")
password = os.getenv("db_password")

conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)

def mark_alert_as_processed(product_id, alert_date):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Inventory_Alerts
        SET is_processed = 1
        WHERE product_id = :1 AND alert_date = :2
    """, (product_id, alert_date))
    conn.commit()