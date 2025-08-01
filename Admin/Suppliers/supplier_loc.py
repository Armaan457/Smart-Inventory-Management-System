import cx_Oracle
import os
from dotenv import load_dotenv
load_dotenv()

def fetch_suppliers_by_location(city=None, country=None):
    dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
    username = os.getenv("db_username")
    password = os.getenv("db_password")

    results = []
    conn = None

    try:
        conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = conn.cursor()
        cursor.callproc("DBMS_OUTPUT.ENABLE")

        # Call the procedure that prints info via DBMS_OUTPUT
        cursor.callproc("GetSuppliersByLocation", [city, country])

        # Fetch lines printed via DBMS_OUTPUT
        statusVar = cursor.var(cx_Oracle.NUMBER)
        lineVar = cursor.var(cx_Oracle.STRING)

        while True:
            cursor.callproc("DBMS_OUTPUT.GET_LINE", (lineVar, statusVar))
            # print(lineVar.getvalue())
            if statusVar.getvalue() != 0:
                break
            results.append(lineVar.getvalue())  

        # Ensure even if no output, return something meaningful
        if not any(results):
            results.append("❌ No output from the procedure.")

    except cx_Oracle.DatabaseError as e:
        results.append(f"❌ Database Error: {str(e)}")
    finally:
        if conn:
            conn.close()

    return results
