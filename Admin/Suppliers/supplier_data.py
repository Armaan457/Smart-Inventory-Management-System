import cx_Oracle
from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

# === Get input from user ===
supplier_name = input("🔍 Enter Supplier Name: ").strip()

try:
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
    )
    print("✅ Connected to Oracle Database.")
    cursor = connection.cursor()

    # Enable DBMS_OUTPUT
    cursor.callproc("DBMS_OUTPUT.ENABLE")

    cursor.callproc("PrintSupplierInfo", [supplier_name])

    statusVar = cursor.var(cx_Oracle.NUMBER)
    lineVar = cursor.var(cx_Oracle.STRING)

    print("\n--- Supplier Details ---")
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
