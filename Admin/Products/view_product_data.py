import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def create_connection():
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

def fetch_product_data_by_name(product_name):
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.product_id,
                    p.name,
                    p.category,
                    p.quantity,
                    p.price,
                    p.sales,
                    p.rating,
                    p.cluster_id,
                    p.supplier_id,
                    s.name AS supplier_name
                FROM Products p
                LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
                WHERE LOWER(p.name) = LOWER(:name)
            """, {'name': product_name})
            result = cursor.fetchone()
            if result:
                columns = ["Product ID", "Name", "Category", "Quantity", "Price", "Sales", "Rating", "Cluster ID", "Supplier ID", "Supplier Name"]
                return dict(zip(columns, result))
            else:
                return {"error": "Product not found."}
    except cx_Oracle.DatabaseError as e:
        return {"error": str(e)}
