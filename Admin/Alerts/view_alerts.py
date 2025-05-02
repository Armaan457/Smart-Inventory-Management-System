import cx_Oracle

def execute_view_alerts(connection):
    cursor = connection.cursor()
    try:
        # =========================================
        # SECTION 1: VIEW specific alert records by product ID and alert date
        # =========================================
        print("Executing SECTION 1: VIEW specific alert records")
        
        # Example query to fetch specific alerts based on product_id and alert_date
        cursor.execute("""
            SELECT * FROM Inventory_Alerts
            WHERE product_id = 101 AND alert_date = TO_DATE('2025-04-30', 'YYYY-MM-DD')
        """)
        inventory_alerts = cursor.fetchall()
        print("Inventory Alerts:", inventory_alerts)

        # You can add more queries here if needed, for example:
        # cursor.execute("SELECT * FROM Inventory_Alerts WHERE alert_date > TO_DATE('2025-01-01', 'YYYY-MM-DD')")
        # alerts_after_jan_2025 = cursor.fetchall()
        # print("Alerts after January 2025:", alerts_after_jan_2025)

    except cx_Oracle.DatabaseError as e:
        print("Error executing view alerts commands:", e)
    finally:
        cursor.close()
