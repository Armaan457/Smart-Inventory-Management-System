import cx_Oracle
import os
from dotenv import load_dotenv
load_dotenv()

# ==========================
# ADMIN: SUPPLIER / CLUSTER
# ==========================
def run_admin_queries(connection):
    cursor = connection.cursor()
    try:
        print("\n🔹 [ADMIN] SUPPLIERS")
        cursor.execute("SELECT * FROM Suppliers")
        print(cursor.fetchall())

        cursor.execute("SELECT name, location FROM Suppliers WHERE location = 'New York'")
        print(cursor.fetchall())

        cursor.execute("SELECT supplier_id, contact_info FROM Suppliers WHERE name LIKE 'Eco%'")
        print(cursor.fetchall())

        print("\n🔹 [ADMIN] CLUSTERS")
        cursor.execute("SELECT * FROM Clusters")
        print(cursor.fetchall())

        cursor.execute("SELECT cluster_id, avg_sales FROM Clusters WHERE avg_sales > 5000")
        print(cursor.fetchall())

        cursor.execute("SELECT cluster_id, avg_popularity_score FROM Clusters WHERE avg_popularity_score < 3.5")
        print(cursor.fetchall())

        print("\n🔹 [ADMIN] PRODUCT COUNT PER SUPPLIER")
        cursor.execute("""
            SELECT s.name AS supplier_name, COUNT(p.product_id) AS product_count
            FROM Suppliers s
            JOIN Products p ON s.supplier_id = p.supplier_id
            GROUP BY s.name
        """)
        print(cursor.fetchall())

        print("\n🔹 [ADMIN] CLUSTERS WITH HIGH AVG SALES")
        cursor.execute("""
            SELECT cluster_id, avg_sales
            FROM Clusters
            GROUP BY cluster_id, avg_sales
            HAVING avg_sales > 10000
        """)
        print(cursor.fetchall())

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"❌ Admin-side error: {error.message}")
    finally:
        cursor.close()


# ==========================
# USER: PRODUCT / USER / TRANSACTION
# ==========================
def run_user_queries(connection):
    cursor = connection.cursor()
    try:
        print("\n🔹 [USER] PRODUCTS")
        cursor.execute("SELECT * FROM Products")
        print(cursor.fetchall())

        cursor.execute("SELECT name, price FROM Products WHERE price > 100")
        print(cursor.fetchall())

        cursor.execute("SELECT name, quantity FROM Products WHERE quantity < 10")
        print(cursor.fetchall())

        cursor.execute("SELECT name, category FROM Products WHERE rating >= 4.0")
        print(cursor.fetchall())

        cursor.execute("SELECT name, sales FROM Products WHERE sales BETWEEN 1000 AND 5000")
        print(cursor.fetchall())

        print("\n🔹 [USER] USERS")
        cursor.execute("SELECT * FROM Users")
        print(cursor.fetchall())

        cursor.execute("SELECT name, role FROM Users WHERE role = 'Admin'")
        print(cursor.fetchall())

        cursor.execute("SELECT user_id, name FROM Users WHERE role IN ('Manager', 'Staff')")
        print(cursor.fetchall())

        print("\n🔹 [USER] TRANSACTIONS")
        cursor.execute("SELECT * FROM Transactions")
        print(cursor.fetchall())

        cursor.execute("""
            SELECT transaction_type, quantity_change, transaction_date
            FROM Transactions
            WHERE transaction_date >= TO_DATE('2025-01-01', 'YYYY-MM-DD')
        """)
        print(cursor.fetchall())

        cursor.execute("SELECT * FROM Transactions WHERE quantity_change < 0 ORDER BY transaction_date DESC")
        print(cursor.fetchall())

        print("\n🔹 [USER] INVENTORY ALERTS")
        cursor.execute("SELECT * FROM Inventory_Alerts")
        print(cursor.fetchall())

        cursor.execute("""
            SELECT product_id, alert_type, message
            FROM Inventory_Alerts
            WHERE is_processed = 0
        """)
        print(cursor.fetchall())

        cursor.execute("SELECT product_id, alert_date FROM Inventory_Alerts WHERE alert_type = 'Low Stock'")
        print(cursor.fetchall())

        print("\n🔹 [USER] JOIN: PRODUCTS WITH SUPPLIERS")
        cursor.execute("""
            SELECT p.product_id, p.name AS product_name, s.name AS supplier_name
            FROM Products p
            JOIN Suppliers s ON p.supplier_id = s.supplier_id
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] JOIN: TRANSACTIONS WITH PRODUCT AND USER")
        cursor.execute("""
            SELECT t.transaction_id, p.name AS product, u.name AS user, t.transaction_type
            FROM Transactions t
            JOIN Products p ON t.product_id = p.product_id
            JOIN Users u ON t.user_id = u.user_id
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] JOIN: INVENTORY ALERTS WITH PRODUCT NAMES")
        cursor.execute("""
            SELECT a.alert_date, a.alert_type, p.name AS product_name
            FROM Inventory_Alerts a
            JOIN Products p ON a.product_id = p.product_id
            WHERE a.is_processed = 0
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] GROUP BY: TOTAL QUANTITY PER CATEGORY")
        cursor.execute("""
            SELECT category, SUM(quantity) AS total_quantity
            FROM Products
            GROUP BY category
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] GROUP BY: TRANSACTION COUNT PER USER")
        cursor.execute("""
            SELECT u.name, COUNT(t.transaction_id) AS total_transactions
            FROM Users u
            JOIN Transactions t ON u.user_id = t.user_id
            GROUP BY u.name
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] GROUP BY + HAVING: CATEGORIES WITH MORE THAN 3 PRODUCTS")
        cursor.execute("""
            SELECT category, COUNT(*) AS num_products
            FROM Products
            GROUP BY category
            HAVING COUNT(*) > 3
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] GROUP BY + HAVING: USERS WITH MORE THAN 5 TRANSACTIONS")
        cursor.execute("""
            SELECT u.name, COUNT(t.transaction_id) AS transaction_count
            FROM Users u
            JOIN Transactions t ON u.user_id = t.user_id
            GROUP BY u.name
            HAVING COUNT(t.transaction_id) > 5
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] ADVANCED: TOP 5 PRODUCTS BY SALES")
        cursor.execute("""
            SELECT name, sales
            FROM Products
            ORDER BY sales DESC
            FETCH FIRST 5 ROWS ONLY
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] ADVANCED: AVERAGE RATING BY CATEGORY")
        cursor.execute("""
            SELECT category, AVG(rating) AS avg_rating
            FROM Products
            GROUP BY category
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] ADVANCED: DAILY TRANSACTION SUMMARY")
        cursor.execute("""
            SELECT transaction_date, SUM(quantity_change) AS total_quantity
            FROM Transactions
            GROUP BY transaction_date
            ORDER BY transaction_date
        """)
        print(cursor.fetchall())

        print("\n🔹 [USER] BONUS: RANK PRODUCTS BY SALES IN EACH CATEGORY")
        cursor.execute("""
            SELECT category, name, sales,
                   RANK() OVER (PARTITION BY category ORDER BY sales DESC) AS rank_in_category
            FROM Products
        """)
        print(cursor.fetchall())

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"❌ User-side error: {error.message}")
    finally:
        cursor.close()


# ==========================
# CONNECTION SETUP + CALLS
# ==========================
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

try:
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn,
    )
    print("✅ Database connection established as SYSDBA.\n")

    # 👇 Run queries here
    run_admin_queries(connection)
    run_user_queries(connection)

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Connection failed: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔚 Database connection closed.")
