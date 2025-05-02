import cx_Oracle

# Oracle DB connection
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = "sys"
password = "Armaan"

# Get input filters from user (optional)
def get_optional_input(prompt):
    val = input(prompt).strip()
    return float(val) if val else None

min_quantity = get_optional_input("Min Avg Quantity (or press Enter to skip): ")
min_price = get_optional_input("Min Avg Price (or press Enter to skip): ")
min_sales = get_optional_input("Min Avg Sales (or press Enter to skip): ")
min_popularity = get_optional_input("Min Popularity Score (or press Enter to skip): ")

try:
    connection = cx_Oracle.connect( 
        user=username,
        password=password,
        dsn=dsn,
        mode=cx_Oracle.SYSDBA
    )
    print("✅ Connected to Oracle Database.")

    cursor = connection.cursor()
    cursor.callproc("DBMS_OUTPUT.ENABLE")

    # Call the filter procedure
    cursor.callproc("FilterClustersByStats", [
        min_quantity,
        min_price,
        min_sales,
        min_popularity
    ])

    # Read DBMS_OUTPUT
    status_var = cursor.var(cx_Oracle.NUMBER)
    line_var = cursor.var(cx_Oracle.STRING)

    print("\n📋 Filtered Cluster Results:\n" + "-" * 40)
    while True:
        cursor.callproc("DBMS_OUTPUT.GET_LINE", (line_var, status_var))
        if status_var.getvalue() != 0:
            break
        print(line_var.getvalue())

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"❌ Database Error: {error.message}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Connection closed.")

