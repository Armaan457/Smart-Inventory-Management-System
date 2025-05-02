import cx_Oracle
from dotenv import load_dotenv
import os
load_dotenv()

def run_modification_queries(connection):
    cursor = connection.cursor()
    try:
        # ===============================
        # ✅ ADMIN SIDE MODIFICATIONS
        # ===============================

        print("\n🔧 Updating relocated supplier addresses...")
        cursor.execute("""
            UPDATE Suppliers
            SET address = '456 Industrial Park', city = 'Newtown', updated_at = SYSDATE
            WHERE relocation_flag = 1
        """)

        print("🔧 Refreshing outdated supplier contact info...")
        cursor.execute("""
            UPDATE Suppliers
            SET phone = '555-0102', email = 'contact@newdomain.com'
            WHERE last_sync < ADD_MONTHS(SYSDATE, -6)
        """)

        print("🔧 Increasing price for understocked products...")
        cursor.execute("""
            UPDATE Products
            SET price = price * 1.10
            WHERE stock_quantity < (
                SELECT reorder_level FROM InventorySettings
                WHERE InventorySettings.category = Products.category
            )
        """)

        print("🔧 Decreasing price for stagnant stock...")
        cursor.execute("""
            UPDATE Products
            SET price = price * 0.95
            WHERE last_sold_date < ADD_MONTHS(SYSDATE, -6)
        """)

        print("🔧 Recalculating cluster average monthly sales...")
        cursor.execute("""
            UPDATE Clusters C
            SET avg_monthly_sales = (
                SELECT NVL(SUM(T.amount), 0) / 30
                FROM Transactions T
                WHERE T.cluster_id = C.cluster_id
                  AND T.transaction_date >= SYSDATE - 30
            )
        """)

        print("🔧 Updating average product price per cluster...")
        cursor.execute("""
            UPDATE Clusters C
            SET avg_price = (
                SELECT AVG(P.price)
                FROM Products P
                WHERE P.cluster_id = C.cluster_id
            )
        """)

        print("🔧 Promoting high-performing users to Admin...")
        cursor.execute("""
            UPDATE Users U
            SET U.role = 'Admin'
            WHERE U.sales > (
                SELECT 1.2 * AVG(sales)
                FROM Users
                WHERE department = U.department
            )
        """)

        print("🔧 Granting admin role to consistently active users...")
        cursor.execute("""
            UPDATE Users
            SET role = 'Admin'
            WHERE performance_rating >= 4.5
              AND last_login >= ADD_MONTHS(SYSDATE, -6)
        """)

        print("🔧 Applying approved corrections to transactions...")
        cursor.execute("""
            UPDATE Transactions T
            SET T.quantity = (
                SELECT C.corrected_quantity
                FROM TransactionCorrections C
                WHERE T.transaction_id = C.transaction_id AND C.approved = 1
            )
            WHERE EXISTS (
                SELECT 1 FROM TransactionCorrections C
                WHERE T.transaction_id = C.transaction_id AND C.approved = 1
            )
        """)

        print("🔧 Processing low stock alerts...")
        cursor.execute("""
            UPDATE Inventory_Alerts
            SET status = 'Processed',
                follow_up_note = 'Restock order placed',
                processed_date = SYSDATE
            WHERE alert_type = 'LowStock' AND status = 'New'
        """)

        print("🔧 Escalating old unprocessed alerts...")
        cursor.execute("""
            UPDATE Inventory_Alerts
            SET status = 'Escalated',
                follow_up_note = 'Escalation: no action taken for 7 days'
            WHERE status = 'New'
              AND SYSDATE - created_at > 7
        """)

        # ============================
        # 👤 USER SIDE MODIFICATIONS
        # ============================

        print("🔧 Correcting negative sale transaction quantities...")
        cursor.execute("""
            UPDATE Transactions
            SET quantity = -quantity
            WHERE transaction_type = 'Sale' AND quantity < 0
        """)

        connection.commit()
        print("\n✅ All modification queries executed successfully.")

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"❌ Database error: {error.message}")
        connection.rollback()
    finally:
        cursor.close()


# ==== Connection Setup ====
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

    run_modification_queries(connection)

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Connection failed: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔚 Database connection closed.")
