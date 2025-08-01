import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("db_username")
password = os.getenv("db_password")

def delete_product(product_id):
    try:
        conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = :1", (product_id,))
        conn.commit()
        return {"success": f"Product ID {product_id} deleted."}
    except Exception as e:
        return {"error": str(e)}

