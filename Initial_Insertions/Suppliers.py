import cx_Oracle
import pandas as pd
import random
from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

csv_file_path = r"Clustering\dataset_dbms.csv"  
df = pd.read_csv(csv_file_path)

unique_suppliers = df['supplier'].dropna().unique()

locations = ['Tokyo, Japan', 'Cupertino, USA', 'Seoul, South Korea', 'Beijing, China', 'Berlin, Germany']
contacts = ['support@company.com', 'help@brand.net', 'info@example.org', 'contact@vendor.com']
phones = ['+81-3-1234-5678', '+1-800-275-2273', '+86-10-9999-8888', '+49-30-4567890']

def random_or_null(choices):
    return random.choice(choices) if random.random() > 0.5 else None

try:
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
    )
    print("Connected to Oracle Database successfully!")
    cursor = connection.cursor()

    for idx, name in enumerate(unique_suppliers, start=1):
        location = random_or_null(locations)
        contact = random_or_null(contacts)
        phone = random_or_null(phones)
        contact_info = f"{contact}, {phone}" if contact and phone else None

        cursor.execute("""
            INSERT INTO Suppliers (supplier_id, name, location, contact_info)
            VALUES (:1, :2, :3, :4)
        """, (idx, name, location, contact_info))
        print(f"Inserted: {name} | Location: {location} | Contact Info: {contact_info}")

    connection.commit()
    cursor.execute("SELECT * FROM Suppliers")
    rows = cursor.fetchall()
    print("\n--- Suppliers in DB ---")
    for row in rows:
        print(row)

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"Database error occurred: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("Database connection closed.")