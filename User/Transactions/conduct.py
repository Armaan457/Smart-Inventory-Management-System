import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def create_connection():
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

def call_conduct_transaction(product_name, quantity, user_id):
    try:
        with create_connection() as conn:
            cursor = conn.cursor()

            cursor.callproc("ConductTransaction", [
                product_name,
                quantity,  # quantity can be positive (stock-in) or negative (stock-out)
                user_id
            ])
            conn.commit()
            return {"success": "Transaction completed successfully."}

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return {"error": error.message}
