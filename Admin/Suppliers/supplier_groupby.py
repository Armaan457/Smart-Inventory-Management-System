# supplier_groupby.py
import cx_Oracle
import os
from dotenv import load_dotenv
load_dotenv()

def fetch_supplier_groupby():
    dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
    username = os.getenv("db_username")
    password = os.getenv("db_password")

    results = []
    try:
        conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT NVL(location, 'Unknown'), COUNT(*) AS total_suppliers
            FROM Suppliers
            GROUP BY location
            HAVING COUNT(*) >= 1
            ORDER BY total_suppliers DESC
        """)
        for location, count in cursor.fetchall():
            results.append((location, count))
    except cx_Oracle.DatabaseError as e:
        results.append((f"Error: {e}",))
    finally:
        if conn:
            conn.close()
    return results
