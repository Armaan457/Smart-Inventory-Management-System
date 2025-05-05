import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def fetch_transactions(user_id=None, is_admin=False):
    try:
        with cx_Oracle.connect(user=username, password=password, dsn=dsn) as conn:
            cursor = conn.cursor()

            if is_admin:
                cursor.execute("""
                    SELECT t.transaction_id, p.name AS product_name, t.transaction_type, 
                           t.quantity_change, t.transaction_date, u.name AS user_name
                    FROM Transactions t
                    JOIN Products p ON t.product_id = p.product_id
                    JOIN User_Data u ON t.user_id = u.user_id
                    ORDER BY t.TRANSACTION_ID asc
                """)
            else:
                
                cursor.execute("""
                    SELECT t.transaction_id, p.name AS product_name, t.transaction_type, 
                           t.quantity_change, t.transaction_date
                    FROM Transactions t
                    JOIN Products p ON t.product_id = p.product_id
                    WHERE t.user_id = :user_id
                    ORDER BY t.TRANSACTION_ID asc
                """, {'user_id': user_id})

            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results

    except cx_Oracle.DatabaseError as e:
        return {"error": str(e)}
