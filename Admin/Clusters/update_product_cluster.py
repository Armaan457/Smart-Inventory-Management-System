import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# Oracle DB setup
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

def update_product_cluster(product_id, new_cluster_id):
    """
    Updates the cluster ID of a specific product.

    Args:
        product_id (int): The ID of the product to be updated.
        new_cluster_id (int): The new cluster ID to assign.

    Returns:
        dict: A message indicating success or describing the error.
    """
    try:
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        # Validate product existence
        cursor.execute("SELECT COUNT(*) FROM Products WHERE product_id = :product_id", {'product_id': product_id})
        if cursor.fetchone()[0] == 0:
            return {"error": f"❌ Product ID {product_id} does not exist."}

        # Validate new cluster existence
        cursor.execute("SELECT COUNT(*) FROM Clusters WHERE cluster_id = :cluster_id", {'cluster_id': new_cluster_id})
        if cursor.fetchone()[0] == 0:
            return {"error": f"❌ Cluster ID {new_cluster_id} does not exist."}

        # Perform the update
        cursor.execute("""
            UPDATE Products
            SET cluster_id = :new_cluster_id
            WHERE product_id = :product_id
        """, {
            'new_cluster_id': new_cluster_id,
            'product_id': product_id
        })
        connection.commit()

        return {"success": f"✅ Product ID {product_id} has been reassigned to Cluster ID {new_cluster_id}."}

    except cx_Oracle.DatabaseError as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()
