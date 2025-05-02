import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def fetch_supplier_info(supplier_name):
    output_lines = []
    try:
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn,
        )
        cursor = connection.cursor()

        # Enable DBMS_OUTPUT
        cursor.callproc("DBMS_OUTPUT.ENABLE")

        # Call the stored procedure
        cursor.callproc("PrintSupplierInfo", [supplier_name])

        statusVar = cursor.var(cx_Oracle.NUMBER)
        lineVar = cursor.var(cx_Oracle.STRING)

        # Read DBMS_OUTPUT lines
        while True:
            cursor.callproc("DBMS_OUTPUT.GET_LINE", (lineVar, statusVar))
            if statusVar.getvalue() != 0:
                break
            output_lines.append(lineVar.getvalue())

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        output_lines.append(f"❌ Database error: {error.message}")

    finally:
        if 'connection' in locals() and connection:
            connection.close()

    return output_lines
