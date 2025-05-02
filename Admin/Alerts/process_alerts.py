import cx_Oracle

def execute_process_alerts(connection):
    cursor = connection.cursor()
    try:
        # =========================================
        # SECTION 1: PROCESS new alert records or updates
        # =========================================
        print("Executing SECTION 1: PROCESS new alert records or updates")

        # Example: Insert a new alert for a specific product
        cursor.execute("""
            INSERT INTO Inventory_Alerts (alert_id, product_id, alert_date, alert_message)
            VALUES (501, 102, TO_DATE('2025-05-01', 'YYYY-MM-DD'), 'Low stock for product 102')
        """)
        print("Inserted a new alert.")

        # Example: Update an existing alert message
        cursor.execute("""
            UPDATE Inventory_Alerts
            SET alert_message = 'Stock replenished for product 101'
            WHERE alert_id = 500
        """)
        print("Updated the alert message for alert_id = 500.")

        # Commit changes to the database
        connection.commit()

    except cx_Oracle.DatabaseError as e:
        print("Error executing process alerts commands:", e)
        connection.rollback()  # Rollback in case of error
    finally:
        cursor.close()
