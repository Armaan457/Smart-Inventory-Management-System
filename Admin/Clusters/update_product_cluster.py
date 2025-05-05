import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# Oracle DB setup
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def reassign_product_cluster(product_id, new_cluster_id):

    try:
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        cursor.callproc("ReassignProductCluster", [product_id, new_cluster_id])
        return {"success": f"✅ Product {product_id} successfully reassigned to cluster {new_cluster_id}."}

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return {"error": f"❌ Oracle Error: {error.message}"}
    
    finally:
        if 'connection' in locals():
            connection.close()
