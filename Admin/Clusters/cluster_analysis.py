import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def filter_clusters(min_quantity=None, min_price=None, min_sales=None, min_popularity=None):
    output_lines = []
    try:
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn,
        )
        cursor = connection.cursor()
        cursor.callproc("DBMS_OUTPUT.ENABLE")

        cursor.callproc("FilterClustersByStats", [
            min_quantity,
            min_price,
            min_sales,
            min_popularity
        ])

        status_var = cursor.var(cx_Oracle.NUMBER)
        line_var = cursor.var(cx_Oracle.STRING)

        while True:
            cursor.callproc("DBMS_OUTPUT.GET_LINE", (line_var, status_var))
            if status_var.getvalue() != 0:
                break
            output_lines.append(line_var.getvalue())

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        output_lines.append(f"❌ Database Error: {error.message}")

    finally:
        if 'connection' in locals() and connection:
            connection.close()

    return output_lines
