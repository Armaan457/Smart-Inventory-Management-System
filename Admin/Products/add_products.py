import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("db_username")
password = os.getenv("db_password")

conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
cursor = conn.cursor()

def add_product(name, category, price, quantity, sales, rating, supplier_id, cluster_id):
    try:
        cursor.execute("SELECT MAX(product_id) FROM products")
        max_id = cursor.fetchone()[0]
        next_id = (max_id or 0) + 1  # Handles empty table

        cursor.execute("""
            INSERT INTO products (product_id, name, category, price, quantity, sales, rating, supplier_id, cluster_id)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
        """, (next_id, name, category, price, quantity, sales, rating, supplier_id, cluster_id))
        conn.commit()
        return {"success": f"Product added with ID {next_id}"}
    except Exception as e:
        return {"error": str(e)}

    
def get_supplier_id_from_name(supplier_name):
    try:
        cursor.execute("SELECT supplier_id FROM suppliers WHERE name = :1", (supplier_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        return None  # or raise if preferred

