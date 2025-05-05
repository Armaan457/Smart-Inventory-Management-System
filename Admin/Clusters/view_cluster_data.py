import cx_Oracle
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Oracle DB setup
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def format_category_distribution(raw_clob):
    # Read and clean the CLOB
    if hasattr(raw_clob, 'read'):
        raw_data = raw_clob.read()
    else:
        raw_data = raw_clob

    try:
        # Try to parse as JSON
        parsed = json.loads(raw_data)
        if isinstance(parsed, dict):
            return [f"{k}: {v}" for k, v in parsed.items()]
        elif isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        # Fall back to comma-separated
        return [entry.strip() for entry in raw_data.split(",") if entry.strip()]

    return [raw_data]  # Fallback

def fetch_cluster_details(cluster_id):
    try:
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT cluster_id, avg_quantity, avg_price, avg_sales, avg_popularity_score, category_distribution
            FROM Clusters
            WHERE cluster_id = :cluster_id
        """, {'cluster_id': cluster_id})

        row = cursor.fetchone()
        if row:
            clean_categories = format_category_distribution(row[5])
            return {
                "Cluster ID": row[0],
                "Average Quantity": row[1],
                "Average Price": row[2],
                "Average Sales": row[3],
                "Popularity Score": row[4],
                "Category Distribution": clean_categories
            }
        else:
            return {"error": f"No cluster found with ID {cluster_id}"}

    except cx_Oracle.DatabaseError as e:
        return {"error": str(e)}
    finally:
        if 'connection' in locals():
            connection.close()
