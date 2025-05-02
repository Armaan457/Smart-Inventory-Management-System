import cx_Oracle

from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

try:
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
    )
    print("✅ Connected to Oracle Database.")
    cursor = connection.cursor()

    query = """
        SELECT location, COUNT(*) AS total_suppliers
        FROM Suppliers
        WHERE location IS NOT NULL
        GROUP BY location
        HAVING COUNT(*) >= 1
    """
    cursor.execute(query)

    # === Fetch and print results ===
    print("\n--- Locations with suppliers ---")
    for location, total in cursor.fetchall():
        print(f"📍 Location: {location} — 🧾 Suppliers: {total}")

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Database error: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Connection closed.")
