import cx_Oracle

from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

# === Get user input from terminal ===
city = input("Enter City (or press Enter to skip): ").strip()
country = input("Enter Country (or press Enter to skip): ").strip()

city = None if city == "" else city
country = None if country == "" else country

try:
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
    )
    print("✅ Connected to Oracle Database.")
    cursor = connection.cursor()

    cursor.callproc("DBMS_OUTPUT.ENABLE")

    cursor.callproc("GetSuppliersByLocation", [city, country])

    statusVar = cursor.var(cx_Oracle.NUMBER)
    lineVar = cursor.var(cx_Oracle.STRING)

    print("\n--- Supplier Info ---")
    while True:
        cursor.callproc("DBMS_OUTPUT.GET_LINE", (lineVar, statusVar))
        if statusVar.getvalue() != 0:
            break
        print(lineVar.getvalue())

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Database error: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Connection closed.")
