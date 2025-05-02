import cx_Oracle
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

csv_file_path = r".\Clustering\dataset_dbms.csv"  
df = pd.read_csv(csv_file_path)

required_columns = [
    'product_id', 'name', 'category',
    'quantity', 'price', 'sales',
    'popularity_score', 'cluster', 'supplier'
]
df = df[required_columns].dropna()

try:
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
    )
    print("✅ Connected to Oracle Database.")
    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO Products (
                product_id, name, category, quantity,
                price, sales, rating, cluster_id, supplier_id
            ) VALUES (
                :1, :2, :3, :4, :5, :6, :7, :8,
                (SELECT supplier_id FROM Suppliers WHERE name = :9)
            )
        """, (
            int(row['product_id']),
            row['name'],
            row['category'],
            int(row['quantity']),
            round(row['price'], 2),
            int(row['sales']),
            round(row['popularity_score'], 2),
            int(row['cluster']),
            row['supplier']  
        ))
        print(f"Inserted product_id {int(row['product_id'])}")

    connection.commit()
    print("\n✅ All products committed to the database.")

    cursor.execute("""
        SELECT
            product_id, name, category, quantity,
            price, sales, rating, cluster_id, supplier_id
        FROM Products
        ORDER BY product_id
    """)
    print("\n--- Products table contents ---")
    for prod in cursor.fetchall():
        print(prod)

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Database error: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Connection closed.")
