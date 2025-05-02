import os
import cx_Oracle
from dotenv import load_dotenv
load_dotenv()

def execute_deletion_commands(connection):
    cursor = connection.cursor()
    try:
        # ========================================
        # SECTION 1: DELETE specific records by ID
        # ========================================
        print("Executing SECTION 1: DELETE specific records by ID")
        cursor.execute("""
            DELETE FROM Inventory_Alerts
            WHERE product_id = 101 AND alert_date = TO_DATE('2025-04-30', 'YYYY-MM-DD')
        """)
        cursor.execute("DELETE FROM Transactions WHERE transaction_id = 1001")
        cursor.execute("DELETE FROM Users WHERE user_id = 501")
        cursor.execute("DELETE FROM Products WHERE product_id = 301")
        cursor.execute("DELETE FROM Clusters WHERE cluster_id = 201")
        cursor.execute("DELETE FROM Suppliers WHERE supplier_id = 101")
        # connection.commit()
        print("SECTION 1 committed successfully.\n")

        # ========================================
        # SECTION 2: DELETE all records (careful!)
        # ========================================
        print("Executing SECTION 2: DELETE all records with conditions")
        cursor.execute("DELETE FROM Products WHERE discontinued = 'Y'")
        cursor.execute("""
            DELETE FROM Transactions
            WHERE transaction_date < SYSDATE - INTERVAL '6' MONTH
        """)
        # Uncomment the following line if you want to delete all users
        # cursor.execute("DELETE FROM Users")
        # connection.commit()
        print("SECTION 2 committed successfully.\n")

        # ========================================
        # SECTION 3: TRUNCATE TABLES
        # ========================================
        print("Executing SECTION 3: TRUNCATE TABLES")
        # Note: TRUNCATE cannot be rolled back in Oracle
        # Child tables must be truncated before parent tables
        cursor.execute("TRUNCATE TABLE Inventory_Alerts")
        cursor.execute("TRUNCATE TABLE Transactions")
        cursor.execute("TRUNCATE TABLE Users")
        cursor.execute("TRUNCATE TABLE Products")
        cursor.execute("TRUNCATE TABLE Clusters")
        cursor.execute("TRUNCATE TABLE Suppliers")
        print("SECTION 3 completed (no commit needed for TRUNCATE).\n")

        # ========================================
        # SECTION 4: DROP TABLES
        # ========================================
        print("Executing SECTION 4: DROP TABLES")
        # Drop child tables first to avoid constraint violations
        cursor.execute("DROP TABLE Inventory_Alerts CASCADE CONSTRAINTS")
        cursor.execute("DROP TABLE Transactions CASCADE CONSTRAINTS")
        cursor.execute("DROP TABLE Users CASCADE CONSTRAINTS")
        cursor.execute("DROP TABLE Products CASCADE CONSTRAINTS")
        cursor.execute("DROP TABLE Clusters CASCADE CONSTRAINTS")
        cursor.execute("DROP TABLE Suppliers CASCADE CONSTRAINTS")
        # connection.commit()
        print("SECTION 4 committed successfully.\n")

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Database error occurred: {error.message}")
        connection.rollback()
    finally:
        cursor.close()

if __name__ == "__main__":
    # Updated connection setup with provided credentials and SYSDBA mode
    dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
    username = os.getenv("username")
    password = os.getenv("password")
    try:
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn,
        )
        print("Database connection established.")
        execute_deletion_commands(connection)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Failed to connect to database: {error.message}")
    finally:
        if 'connection' in locals():
            connection.close()
            print("Database connection closed.")
