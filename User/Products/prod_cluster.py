import cx_Oracle
from dotenv import load_dotenv
import os
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("db_username")
password = os.getenv("db_password")


def recommend_items_by_category(category):
    try:
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn,
        )
        cursor = connection.cursor()
        cursor.callproc("DBMS_OUTPUT.ENABLE")

        cursor.callproc("RecommendItemsByCategory", [category])
        
        status_var = cursor.var(cx_Oracle.NUMBER)
        line_var = cursor.var(cx_Oracle.STRING)

        output_lines = []
        while True:
            cursor.callproc("DBMS_OUTPUT.GET_LINE", (line_var, status_var))
            if status_var.getvalue() != 0:
                break
            output_lines.append(line_var.getvalue())

        return output_lines

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return [f"❌ Database Error: {error.message}"]

    finally:
        if 'connection' in locals() and connection:
            connection.close()

