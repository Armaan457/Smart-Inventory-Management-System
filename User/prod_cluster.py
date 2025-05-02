import cx_Oracle
from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

# Input from user
category = input("Enter the product category: ").strip()

try:
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
        mode=cx_Oracle.SYSDBA
    )
    print("✅ Connected to Oracle Database.")

    cursor = connection.cursor()
    cursor.callproc("DBMS_OUTPUT.ENABLE")

    cursor.callproc("RecommendItemsByCategory", [category])
    
    status_var = cursor.var(cx_Oracle.NUMBER)
    line_var = cursor.var(cx_Oracle.STRING)

    print("\n📋 Results:\n" + "-" * 40)
    while True:
        cursor.callproc("DBMS_OUTPUT.GET_LINE", (line_var, status_var))
        if status_var.getvalue() != 0:
            break
        print(line_var.getvalue())

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Database Error: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Connection closed.")
